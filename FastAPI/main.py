from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models import Order, Base
from database import get_db, engine
from auth import get_password_hash, verify_password
from services.user_service import UserService
from services.order_service import OrderService
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if request.headers.get("accept") == "application/json":
        return await http_exception_handler(request, exc)

    error_html = f"""
    <script>
        alert("{exc.detail}");
        window.history.back();
    </script>
    """
    return HTMLResponse(content=error_html, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "Ошибка валидации: " + str(exc.errors())
    error_html = f"""
    <script>
        alert("{error_msg}");
        window.history.back();
    </script>
    """
    return HTMLResponse(content=error_html, status_code=400)

class AuthHandler:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    async def register(self, name: str, email: str, password: str):
        if self.user_service.get_user_by_email(email):
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        hashed_password = get_password_hash(password)
        self.user_service.create_user(name, email, hashed_password)
        return RedirectResponse(url="/", status_code=303)

    async def login(self, email: str, password: str):
        user = self.user_service.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Неверный email или пароль")
        response = RedirectResponse(url="/personal_account", status_code=303)
        response.set_cookie(key="user_email", value=email)
        return response

    async def logout(self):
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie(key="user_email")
        return response

class OrderHandler:
    def __init__(self, db: Session):
        self.db = db
        self.order_service = OrderService(db)

    async def view_pending_orders(self, request: Request):
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Необходимо войти в систему")
        orders = self.order_service.get_pending_orders_by_email(user_email)
        return templates.TemplateResponse(
            "my_orders.html",
            {"request": request, "orders": orders, "status": "Заказы в очереди"}
        )

    async def perform_order(self, order_id: int):
        order = self.order_service.update_order_status(order_id, "Processed")
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return RedirectResponse(url="/pending_orders", status_code=303)

    async def view_processed_orders(self, request: Request):
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Необходимо войти в систему")
        orders = self.order_service.get_processed_orders_by_email(user_email)
        return templates.TemplateResponse(
            "my_orders.html",
            {"request": request, "orders": orders, "status": "Завершенные заказы", "active_button": "processed", "delete_btn": "yes"}
        )

    async def delete_processed_orders(self, request: Request):
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Необходимо войти в систему")
        deleted_count = self.order_service.delete_processed_orders_by_email(user_email)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Нет завершенных заказов для удаления")
        return RedirectResponse(url="/processed_orders", status_code=303)

    async def create_order(self, email: str, status: str, description: str):
        if not email:
            raise HTTPException(status_code=400, detail="Необходимо ввести email пользователя")
        new_order = self.order_service.append_new_order(email, status, description)
        return RedirectResponse(url="/create_order", status_code=303)



@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_handler = AuthHandler(db)
    return await auth_handler.register(name, email, password)

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = None
):
    auth_handler = AuthHandler(db)
    return await auth_handler.login(email, password)

@app.get("/personal_account", response_class=HTMLResponse)
async def personal_account(request: Request):
    return templates.TemplateResponse("personal_account.html", {"request": request})

@app.get("/logout")
async def logout(db: Session = Depends(get_db)):
    auth_handler = AuthHandler(db)
    return await auth_handler.logout()


@app.post("/personal_account")
async def process_choice(choice: str = Form(...)):
    if choice == 'my_orders':
        return RedirectResponse(url="/pending_orders", status_code=303)
    if choice == 'create_order':
        return RedirectResponse(url="/create_order", status_code=303)

@app.get("/pending_orders", response_class=HTMLResponse)
async def view_pending_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    order_handler = OrderHandler(db)
    return await order_handler.view_pending_orders(request)

@app.get("/perform")
async def perform_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order_handler = OrderHandler(db)
    return await order_handler.perform_order(order_id)

@app.get("/processed_orders", response_class=HTMLResponse)
async def view_processed_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    order_handler = OrderHandler(db)
    return await order_handler.view_processed_orders(request)

@app.get("/delete_processed")
async def delete_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    order_handler = OrderHandler(db)
    return await order_handler.delete_processed_orders(request)

@app.get("/create_order", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("create_order.html", {"request": request})

@app.post("/create_order")
async def create_new(
    db: Session = Depends(get_db),
    email: str = Form(...),
    description: str = Form(...)
):
    order_handler = OrderHandler(db)
    return await order_handler.create_order(email, description, "Pending")