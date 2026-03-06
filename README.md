# IPL Auction Quotation System

A college-ready Python project built with **Flask + PostgreSQL**.

## Features
- Cricket-themed frontend with player cards/table
- Stores IPL players in a database
- Search players by name
- Filter by nationality, role, and team
- Shows player details like strike rate, team, role, and quotation
- Shows all Indian players when filter is set to `Indian`
- Auction starting price is stored for every player
- **Business rule:** quotation can only move upward, never downward
- Bid history for each player
- Ready for Render deployment

## Tech Stack
- Python
- Flask
- PostgreSQL
- SQLAlchemy ORM
- Bootstrap 5
- Gunicorn
- Render

## Project Structure
```text
ipl_auction_app/
│── app.py
│── requirements.txt
│── runtime.txt
│── render.yaml
│── .env.example
│── README.md
│── templates/
│   ├── base.html
│   ├── index.html
│   └── player_detail.html
└── static/
    └── css/
        └── style.css
```

## How to run locally
### 1) Create virtual environment
```bash
python -m venv venv
```

### 2) Activate virtual environment
#### Windows
```bash
venv\Scripts\activate
```

#### macOS / Linux
```bash
source venv/bin/activate
```

### 3) Install requirements
```bash
pip install -r requirements.txt
```

### 4) Set environment variables
Create a `.env` file or export these variables manually:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://username:password@localhost:5432/ipl_auction_db
```

If you do not have PostgreSQL locally, the app will still run with SQLite by default for demo/testing.

### 5) Run the app
```bash
python app.py
```

Open:
```text
http://127.0.0.1:5000
```

## PostgreSQL database setup
```sql
CREATE DATABASE ipl_auction_db;
```

Then use this DATABASE_URL format:
```text
postgresql://postgres:yourpassword@localhost:5432/ipl_auction_db
```

## GitHub push commands
```bash
git init
git add .
git commit -m "Initial commit - IPL Auction Quotation System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## Render deployment steps
1. Push project to GitHub.
2. Sign in to Render.
3. Click **New +** → **Blueprint**.
4. Select your GitHub repo.
5. Render will read `render.yaml`.
6. It will create:
   - Web service
   - PostgreSQL database
7. After deployment, open the Render URL.

## Important project logic
In the bid route:
- Bid cannot be lower than auction starting price
- Bid cannot be lower than current price
- Bid cannot be equal to current price
- New quote must be higher than current quote

## Suggested viva explanation
"This software is an IPL auction quotation management system. It stores player data in PostgreSQL, supports filtering by nationality like Indian players, displays strike rate and auction details, and enforces a rule that quotations can only increase from the starting price. The frontend is built using Flask templates and Bootstrap, and the application is deployment-ready on Render."

## Notes
- The project includes a seeded demo dataset of popular IPL players.
- You can add more players directly in the `SEED_PLAYERS` list or build an admin form later.
