# Deployment Guide

This guide covers multiple deployment options for your HCI experiment platform.

## Quick Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

**Best for**: Easy deployment with free tier, good for research projects

#### Backend Deployment (Render)

1. **Create a Render account**: https://render.com

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Choose "Web Service"
   - Name: `hci-experiment-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Instance Type: Free tier

3. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4
   DATABASE_URL=postgresql://... (Render provides this)
   SECRET_KEY=your-secret-key-here
   ```

4. **Add Build Script** (`backend/render-build.sh`):
   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   python preprocess_data.py
   ```

#### Frontend Deployment (Render)

1. **Create a Static Site**:
   - Connect GitHub repository
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

2. **Set Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

### Option 2: Railway (Recommended - Easy Full-Stack)

**Best for**: Full-stack deployment in one place

1. **Create Railway account**: https://railway.app

2. **Deploy Backend**:
   - New Project → Deploy from GitHub
   - Select repository
   - Add Service → Python
   - Root Directory: `backend`
   - Railway will auto-detect requirements.txt
   - Set environment variables (same as Render)

3. **Deploy Frontend**:
   - Add Service → Static Files
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`

### Option 3: Vercel (Frontend) + Railway/Render (Backend)

**Best for**: Best performance for frontend

#### Frontend on Vercel:
1. Install Vercel CLI: `npm i -g vercel`
2. In `frontend/` directory: `vercel`
3. Set environment variable: `VITE_API_URL=https://your-backend-url`

#### Backend:
Use Railway or Render (see above)

## Required Files for Deployment

### Backend Files Needed

1. **Procfile** (for Heroku/Railway):
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

2. **runtime.txt** (optional, specify Python version):
   ```
   python-3.12.0
   ```

3. **gunicorn** in requirements.txt (for production server)

### Frontend Configuration

Update `vite.config.js` to use environment variable for API URL:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
```

## Step-by-Step: Render Deployment

### 1. Prepare Backend

Create `backend/Procfile`:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

Update `backend/requirements.txt` to include:
```
gunicorn
```

### 2. Prepare Frontend

Update `frontend/vite.config.js` for production:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
```

### 3. Deploy Backend on Render

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `hci-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python preprocess_data.py`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add Environment Variables:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL=gpt-4`
   - `SECRET_KEY` (generate random string)
   - `DATABASE_URL` (Render provides PostgreSQL URL)
6. Click "Create Web Service"
7. Note the URL: `https://hci-backend.onrender.com`

### 4. Deploy Frontend on Render

1. Click "New +" → "Static Site"
2. Connect GitHub repository
3. Configure:
   - **Name**: `hci-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL=https://hci-backend.onrender.com`
5. Click "Create Static Site"
6. Your app will be available at: `https://hci-frontend.onrender.com`

### 5. Update Frontend API Configuration

After deployment, update frontend to use the backend URL:

Create `frontend/.env.production`:
```
VITE_API_URL=https://hci-backend.onrender.com
```

## Database Setup

### Option A: PostgreSQL (Recommended for Production)

Render/Railway provide PostgreSQL databases:
1. Create PostgreSQL database in Render/Railway
2. Get connection URL
3. Set `DATABASE_URL` environment variable
4. Update `backend/app.py` to use PostgreSQL:
   ```python
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

### Option B: Keep SQLite (Simple but Limited)

- Works for small-scale testing
- Not recommended for production
- Database file needs to persist (use volumes in Railway)

## Post-Deployment Checklist

1. ✅ Backend is running and accessible
2. ✅ Frontend can connect to backend
3. ✅ Database is initialized (run `preprocess_data.py`)
4. ✅ Environment variables are set
5. ✅ CORS is configured correctly
6. ✅ Test the app end-to-end

## Testing Deployment

1. **Test Backend**:
   ```bash
   curl https://your-backend-url.onrender.com/api/health
   ```

2. **Test Frontend**:
   - Visit your frontend URL
   - Try creating a participant
   - Test a search query

## Troubleshooting

### Backend Issues
- Check logs in Render/Railway dashboard
- Verify environment variables are set
- Ensure `gunicorn` is in requirements.txt
- Check database connection

### Frontend Issues
- Verify `VITE_API_URL` is set correctly
- Check browser console for CORS errors
- Ensure build completed successfully

### Database Issues
- Run `preprocess_data.py` after deployment
- Check database connection string
- Verify tables exist

## Security Considerations

1. **Never commit `.env` files**
2. **Use strong SECRET_KEY**
3. **Set CORS origins properly** (limit to your frontend domain)
4. **Use HTTPS** (Render/Railway provide this automatically)
5. **Protect OpenAI API key** (use environment variables)

## Cost Estimates

- **Render Free Tier**: Free (with limitations)
- **Railway Free Tier**: $5/month credit (usually free for small apps)
- **Vercel**: Free for frontend
- **Total**: ~$0-5/month for research project

## Quick Start Commands

```bash
# 1. Add gunicorn to requirements.txt
echo "gunicorn" >> backend/requirements.txt

# 2. Create Procfile
echo "web: gunicorn app:app --bind 0.0.0.0:\$PORT" > backend/Procfile

# 3. Commit and push to GitHub
git add .
git commit -m "Add deployment configuration"
git push

# 4. Deploy on Render/Railway (follow UI instructions)
```

