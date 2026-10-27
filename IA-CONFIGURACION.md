# GEARS RADAR · Resúmenes en español con IA

La sección **Resumen IA en español** ya se muestra en la página pública. Para que genere contenido real hace falta agregar una clave de OpenAI como secreto de GitHub Actions.

1. Obtén una clave API en https://platform.openai.com/api-keys (la API se factura independientemente de ChatGPT).
2. En el repositorio ve a **Settings → Secrets and variables → Actions → New repository secret**.
3. En **Name** escribe exactamente `OPENAI_API_KEY` y pega tu clave en **Secret**. Nunca la escribas en archivos, chat o capturas.
4. En **Actions → Actualizar noticias GEARS RADAR → Run workflow** elige `main` y ejecuta.
5. Abre la página pública; después de concluir el workflow verás el resumen y los guiones en español.

El workflow se ejecuta cuatro veces al día. El script `generate_editorial.py` envía títulos y extractos de un máximo de 65 publicaciones recientes al modelo `gpt-4.1-mini` y publica `data/editorial.json`. No envía conversaciones privadas. Si falla o falta la clave, se conserva el último resultado válido. **No** genera un guion a demanda desde la web; publica hasta tres propuestas por actualización. Los enlaces de las fuentes originales mantienen su idioma. El resumen y los guiones están en español.

Precauciones: la síntesis usa titulares y extractos, no vídeos completos. Revisa las fuentes antes de afirmar acusaciones o rumores. En GitHub Actions puedes desactivar el workflow para detener el costo recurrente. Recomendado fijar límites de presupuesto y de uso en la cuenta de OpenAI.
