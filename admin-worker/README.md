# Administrador seguro de GEARS RADAR

Este directorio contiene un backend Cloudflare Worker para administrar la lista pública de creadores. GitHub Pages **no permite ocultar claves en JavaScript**, así que el acceso usa un Worker privado y los secretos de Cloudflare.

## Configurar

1. Crea una cuenta en Cloudflare y un Worker llamado `gears-radar-admin`.
2. Publica el código de `worker.js` como Worker (por Dashboard o Wrangler).
3. Configura tres **Secrets** (no variables públicas): `ADMIN_PASSWORD` con el código acordado, `SESSION_SECRET` con una cadena aleatoria larga y `GITHUB_TOKEN` con un token fine-grained de GitHub limitado **únicamente** a `OC-apps/gears-radar` con permiso Contents: Read and Write.
4. Abre `https://oc-apps.github.io/gears-radar/admin.html`; introduce la URL HTTPS del Worker y tu contraseña.
5. Agrega o edita creadores y pulsa **Guardar cambios públicos**. El Worker modifica `creadores.json` y GitHub Pages muestra después la nueva lista.

**Limitaciones actuales:** el acceso se valida en el servidor y genera un token temporal de una hora. No hay límite de intentos de contraseña integrado; antes de uso público configura una regla de Cloudflare WAF / rate limiting para `/login`. No publiques jamás el token de GitHub ni el código de acceso. La lista pública de creadores es distinta de la lista personal local de cada visitante. El RSS se actualiza conforme al workflow existente. No hay aún edición segura de noticias o categorías desde el panel.

Si necesitas rotar el código, cambia solamente el secreto `ADMIN_PASSWORD` desde Cloudflare. Para invalidar todas las sesiones, rota también `SESSION_SECRET`.
