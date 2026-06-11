from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import (
    create_tables,
    create_user,
    get_user_by_email,
    get_jobs,
    create_job,
    add_application,
    hash_password,
)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="replace-with-a-secure-random-key")

templates = Jinja2Templates(directory="templates")


def render_template(request: Request, name: str, context: dict):
    context["request"] = request
    import inspect
    sig = inspect.signature(templates.TemplateResponse)
    if "request" in sig.parameters:
        return templates.TemplateResponse(request=request, name=name, context=context)
    else:
        return templates.TemplateResponse(name, context)


ADMIN_EMAIL = "admin@college.com"
ADMIN_PASSWORD = "admin123"


def flash(request: Request, message: str):
    request.session["flash"] = message


def get_flash(request: Request):
    return request.session.pop("flash", None)


def current_user(request: Request):
    return request.session.get("user")


@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template(
        request,
        "login.html",
        {"message": get_flash(request)}
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render_template(
        request,
        "register.html",
        {"message": get_flash(request)}
    )


@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    existing_user = get_user_by_email(email)
    if existing_user:
        flash(request, "This email is already registered. Please login.")
        return RedirectResponse("/register", status_code=303)

    create_user(name, email, hash_password(password))
    flash(request, "Registration successful. Please login.")
    return RedirectResponse("/", status_code=303)


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        request.session["user"] = {
            "name": "Admin",
            "email": ADMIN_EMAIL,
            "is_admin": True,
        }
        return RedirectResponse("/admin", status_code=303)

    user = get_user_by_email(email)
    if not user or user["password"] != hash_password(password):
        flash(request, "Invalid email or password.")
        return RedirectResponse("/", status_code=303)

    request.session["user"] = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "is_admin": False,
    }
    return RedirectResponse("/jobs", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    flash(request, "You have been logged out.")
    return RedirectResponse("/", status_code=303)


@app.get("/jobs", response_class=HTMLResponse)
def jobs_page(request: Request):
    user = current_user(request)
    if not user:
        flash(request, "Please login first.")
        return RedirectResponse("/", status_code=303)

    return render_template(
        request,
        "jobs.html",
        {
            "jobs": get_jobs(),
            "user": user,
            "message": get_flash(request),
        },
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    user = current_user(request)
    if not user or not user.get("is_admin"):
        flash(request, "Admin access is required.")
        return RedirectResponse("/", status_code=303)

    return render_template(
        request,
        "admin.html",
        {"user": user, "message": get_flash(request)},
    )


@app.post("/add-job")
def add_job(
    request: Request,
    title: str = Form(...),
    company: str = Form(...),
    description: str = Form(...),
):
    user = current_user(request)
    if not user or not user.get("is_admin"):
        flash(request, "Admin access is required.")
        return RedirectResponse("/", status_code=303)

    create_job(title, company, description)
    flash(request, "Job posted successfully.")
    return RedirectResponse("/jobs", status_code=303)


@app.post("/apply/{job_id}")
def apply_job(request: Request, job_id: int):
    user = current_user(request)
    if not user or user.get("is_admin"):
        flash(request, "Please login as a student to apply.")
        return RedirectResponse("/", status_code=303)

    if add_application(user["id"], job_id):
        flash(request, "Application submitted successfully.")
    else:
        flash(request, "You have already applied for this job.")

    return RedirectResponse("/jobs", status_code=303)
