# Quick Deployment Guide

## Fastest Option: Render (Free Tier)

### Step 1: Prepare Repository

Make sure your code is on GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy Backend (5 minutes)

1. Go to https://render.com
2. Sign up/login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `hci-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Add Environment Variables:
   - `OPENAI_API_KEY` = your OpenAI key
   - `OPENAI_MODEL` = `gpt-4`
   - `SECRET_KEY` = generate random string
7. Click "Create Web Service"
8. Wait for deployment (~5 minutes)
9. **Copy the URL**: `https://hci-backend-xxxx.onrender.com`

### Step 3: Initialize Database

After backend deploys, run database initialization:

1. Go to Render dashboard → Your backend service
2. Click "Shell" tab
3. Run:
   ```bash
   python preprocess_data.py
   python generate_ground_truth.py
   ```

### Step 4: Deploy Frontend (5 minutes)

1. In Render dashboard, click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `hci-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `https://hci-backend-xxxx.onrender.com` (your backend URL)
5. Click "Create Static Site"
6. **Your app URL**: `https://hci-frontend-xxxx.onrender.com`

### Step 5: Share the Link!

Send participants: `https://hci-frontend-xxxx.onrender.com`

## Alternative: Railway (Even Easier)

1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Select your repository
4. Railway auto-detects:
   - Backend: Python service
   - Frontend: Static site
5. Add environment variables
6. Done!

## Environment Variables Checklist

### Backend:
- ✅ `OPENAI_API_KEY`
- ✅ `OPENAI_MODEL=gpt-4`
- ✅ `SECRET_KEY` (random string)
- ✅ `DATABASE_URL` (auto-provided by Render/Railway)

### Frontend:
- ✅ `VITE_API_URL` (your backend URL)

## Post-Deployment

1. Test backend: `curl https://your-backend-url/api/health`
2. Visit frontend URL
3. Create a test participant
4. Run through one task
5. Check logs if issues occur

## Troubleshooting

**Backend won't start:**
- Check logs in Render/Railway dashboard
- Verify `gunicorn` is in requirements.txt
- Check environment variables

**Frontend can't connect:**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Check browser console for errors

**Database empty:**
- Run `python preprocess_data.py` in backend shell
- Run `python generate_ground_truth.py`

## Cost

- **Render Free Tier**: Free (with some limitations)
- **Railway**: $5/month credit (usually free for small apps)
- **Total**: $0/month for research project

