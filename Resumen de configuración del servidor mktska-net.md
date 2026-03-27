# Resumen de configuración del servidor mktska.net

**Servidor:** AWS EC2 — Ubuntu — IP `98.85.130.94`

---

## Servicios que corren

| Servicio | Rol | Ubicación |
|---|---|---|
| **Nginx** | Proxy inverso + SSL | `/etc/nginx/sites-available/mitienda` |
| **Gunicorn** | Servidor Django (Python) | Socket: `/run/gunicorn/gunicorn.sock` |
| **Certbot** | Certificados SSL (Let's Encrypt) | `/etc/letsencrypt/live/mktska.net/` |

---

## Rutas del proyecto en EC2

| Qué | Ruta |
|---|---|
| Frontend Vue (dist) | `/var/www/mitienda/frontend/dist` |
| Backend Django | `/var/www/mitienda/backend` |
| Static files | `/var/www/mitienda/backend/staticfiles/` |
| Media (imágenes) | `/var/www/mitienda/backend/media/` |

---

## Cómo reiniciar cada servicio

### Nginx
```bash
sudo systemctl reload nginx    # recarga config sin downtime
sudo systemctl restart nginx   # reinicio completo
sudo nginx -t                  # verificar config antes de reiniciar
```

### Gunicorn
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn       # ver si está corriendo
sudo journalctl -u gunicorn -n 50    # ver logs recientes
```

### Ambos a la vez (deploy típico)
```bash
sudo systemctl restart gunicorn && sudo systemctl reload nginx
```

---

## Flujo de deploy cuando haces cambios

```bash
# En EC2:
cd /var/www/mitienda/backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt           # si hay nuevas dependencias
python manage.py migrate                  # si hay migraciones
python manage.py collectstatic --no-input # si hay archivos estáticos nuevos
sudo systemctl restart gunicorn
```

---

## Ver logs en tiempo real

```bash
sudo journalctl -u gunicorn -f         # logs de Django en vivo
sudo tail -f /var/log/nginx/error.log  # errores de Nginx
```
