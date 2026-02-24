# FB Number Lookup

Ứng dụng Flask tra cứu thông tin Facebook từ số điện thoại thông qua API fbnumber.com.

## Cài đặt

```bash
pip install flask requests
```

## Chạy

```bash
python app.py
```

Server chạy tại: **http://127.0.0.1:5559/**

## Sử dụng

### Giao diện Web

Truy cập `http://127.0.0.1:5559/` để sử dụng giao diện tra cứu:

1. **Nhập Token** — Dán Bearer token và bấm "Lưu Token"
2. **Nhập SĐT** — Nhập số điện thoại và bấm "Tra cứu"
3. **Xem kết quả** — Hiển thị thông tin Facebook (avatar, tên, UID, link profile)

### API

#### Cập nhật token

```bash
curl -X POST http://127.0.0.1:5559/api/token \
  -H 'Content-Type: application/json' \
  -d '{"token": "eyJhbGciOi..."}'
```

#### Tra cứu số điện thoại

```bash
curl 'http://127.0.0.1:5559/api/search?phone=0912185198'
```

#### Xem token hiện tại

```bash
curl http://127.0.0.1:5559/api/token
```
# is-exist-sdt-facebook
