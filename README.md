# auth-service
Microservice for secure registration and authorization of AtlasID users

RestAPI python приложение, управляющее пользователями. Позволяет регистрировать и авторизовывать пользователей в системе AtlasID.

## Необходимо:
- PostgreSQL 13+
- Python 3.12
- requirements.txt

## Использование:
### 1. Регистрация

### **POST** `/signup`
#### Описание:
Регистрация нового пользователя.

#### Запрос:
```json
{
  "nickname": "user123",
  "email": "user@example.com",
  "password": "securepassword123",
  "password_confirmation": "securepassword123"
}
```

#### Ответ (успех):
- **HTTP 201 Created**
```json
{
  "id": 1,
  "nickname": "user123",
  "email": "user@example.com",
  "is_active": true
}
```

#### Ответ (ошибка):
- **HTTP 400 Bad Request**
```json
{
  "detail": "Email already exists"
}
```

---

### 2. Авторизация

### **POST** `/login`
#### Описание:
Авторизация пользователя по email или nickname и паролю.

#### Запрос:
```json
{
  "login": "user123",
  "password": "securepassword123"
}
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg==",
  "token_type": "bearer"
}
```

#### Ответ (ошибка):
- **HTTP 401 Unauthorized**
```json
{
  "detail": "Invalid credentials"
}
```

---

### 3. Обновление токена

### **POST** `/token/refresh`
#### Описание:
Обновление access токена с использованием refresh токена.

#### Запрос:
```json
{
  "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg=="
}
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

#### Ответ (ошибка):
- **HTTP 401 Unauthorized**
```json
{
  "detail": "Invalid or expired refresh token"
}
```

---

### 4. Выход из системы (отзыв токенов)

### **POST** `/logout`
#### Описание:
Отзыв refresh токена для завершения сессии.

#### Запрос:
```json
{
  "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg=="
}
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "detail": "Token revoked successfully"
}
```

#### Ответ (ошибка):
- **HTTP 400 Bad Request**
```json
{
  "detail": "Token not found or already revoked"
}
```

---

### 5. Получение информации о пользователе

### **GET** `/users/me`
#### Описание:
Получение информации о текущем пользователе.

#### Заголовок:
```http
Authorization: Bearer <access_token>
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "id": 1,
  "nickname": "user123",
  "email": "user@example.com",
  "is_active": true,
  "role": "user"
}
```

#### Ответ (ошибка):
- **HTTP 401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

---

### 6. Обновление профиля пользователя

### **PUT** `/users/me`
#### Описание:
Обновление информации текущего пользователя (например, пароля или email).

#### Заголовок:
```http
Authorization: Bearer <access_token>
```

#### Запрос:
```json
{
  "email": "newemail@example.com",
  "password": "newpassword123"
}
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "id": 1,
  "nickname": "user123",
  "email": "newemail@example.com",
  "is_active": true,
  "role": "user"
}
```

#### Ответ (ошибка):
- **HTTP 400 Bad Request**
```json
{
  "detail": "Invalid email format"
}
```

---

### 7. Удаление профиля пользователя

### **DELETE** `/users/me`
#### Описание:
Удаление текущего пользователя.

#### Заголовок:
```http
Authorization: Bearer <access_token>
```

#### Ответ (успех):
- **HTTP 204 No Content**

#### Ответ (ошибка):
- **HTTP 401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

---

### 8. Аутентификация через OAuth

### **GET** `/oauth/{provider}`
#### Описание:
Инициация OAuth-потока для внешнего провайдера.

#### Пример запроса:
```http
GET /oauth/google
```

#### Ответ (успех):
- **HTTP 302 Found**
  Редирект на страницу авторизации провайдера.

#### Ответ (ошибка):
- **HTTP 400 Bad Request**
```json
{
  "detail": "Unsupported OAuth provider"
}
```

---

### **GET** `/oauth/{provider}/callback`
#### Описание:
Обработка ответа от OAuth провайдера.

#### Пример запроса:
```http
GET /oauth/google/callback?code=AUTH_CODE
```

#### Ответ (успех):
- **HTTP 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbg==",
  "token_type": "bearer"
}
```

#### Ответ (ошибка):
- **HTTP 400 Bad Request**
```json
{
  "detail": "Invalid authorization code"
}
```