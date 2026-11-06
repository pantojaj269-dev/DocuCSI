# Guía de Despliegue en la Nube: DocuCSI

Esta guía explica la arquitectura de despliegue en la nube para **DocuCSI** y por qué está configurado de esta manera.

---

## 1. Arquitectura Recomendada: Frontend en Vercel + Backend en Render / Hugging Face

### ¿Por qué esta arquitectura?
- **Frontend (React + Vite + Tailwind CSS):** Pesa menos de 2 MB compilado. Es ideal para **Vercel**, obteniendo despliegues automáticos con cada `git push` y CDN global ultrarrápida.
- **Backend (FastAPI + PyTorch + OpenCV + Scikit-Learn):** Utiliza bibliotecas nativas de C++ y modelos de Deep Learning que pesan más de **1.5 GB**. 
  > **Nota Técnica:** Las *Serverless Functions* de Vercel tienen un límite estricto de **250 MB**. Por eso, ningún backend con PyTorch o visión computacional completa puede ejecutarse dentro de Vercel directamente sin crashear. La solución estándar en la industria es alojar el backend en un servicio con soporte para contenedores Docker.

---

## 2. Paso a Paso para Desplegar

### Paso A: Subir el código a GitHub
1. Inicializa tu repositorio (ya está listo localmente con `.gitignore`):
   ```bash
   git add .
   git commit -m "feat: DocuCSI suite forense completa"
   ```
2. Crea un repositorio en [GitHub](https://github.com/new).
3. Conéctalo y súbelo:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git branch -M main
   git push -u origin main
   ```

---

### Paso B: Desplegar el Backend (Gratis en Render o Hugging Face)

#### Opción 1: Render.com (Recomendado)
1. Entra a [render.com](https://render.com/) e inicia sesión con GitHub.
2. Haz clic en **New +** -> **Web Service**.
3. Selecciona tu repositorio de GitHub.
4. Configuración:
   - **Root Directory:** `Backend`
   - **Environment:** `Docker` (usará automáticamente el `Backend/Dockerfile` que ya dejamos listo).
   - **Plan:** Free
5. Haz clic en **Deploy Web Service**.
6. Una vez terminado, Render te dará una URL HTTPS como:
   `https://docucsi-backend.onrender.com`

---

### Paso C: Desplegar el Frontend en Vercel
1. Entra a [vercel.com](https://vercel.com/) e inicia sesión con GitHub.
2. Haz clic en **Add New...** -> **Project**.
3. Importa tu repositorio de DocuCSI.
4. En **Framework Preset**, selecciona **Vite**.
5. En **Root Directory**, selecciona `Frontend` (o deja la raíz si usa el `vercel.json` configurado).
6. En **Environment Variables**, añade:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://docucsi-backend.onrender.com` (la URL de tu backend en Render).
7. Haz clic en **Deploy**. ¡Listo! Tu proyecto estará en `https://tu-proyecto.vercel.app`.

---

## 3. Acceso Inmediato por Túnel (Sin Despliegue en la Nube)

Si necesitas probar el proyecto ahora mismo desde cualquier teléfono o computadora sin configurar cuentas en la nube:
- Mantén el backend y frontend corriendo localmente.
- El túnel público activo es:
  **`https://a80fda9216222e.lhr.life`**
