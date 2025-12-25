# Dueable – An Assignment Tracker

**Team PixelATE:** Nyah • Kultum • Kayla • Taylor • Olivia  
**Course:** CS 370 – Computer Science Practicum (Software Development)

Dueable is a smart assignment tracker that helps students stay on top of their semester without manually typing every due date. Upload a syllabus (PDF, screenshot, or pasted text), and the app parses assignments, due dates, and class info, then drops them straight into a calendar-style planner.

---

## Live Demo

**Web App:** https://pixelate-nkkto.netlify.app/login  

> **Tip:** Use the app in a private/incognito window for the smoothest experience.  
> The UI is designed with mobile in mind, but the Netlify web build is provided so anyone can try it easily.

---

## What Dueable Does

- **Syllabus Upload**
  - Upload PDF syllabi, screenshots, or paste raw text.
  - The app parses assignments, due dates, and course names automatically.

- **AI-Assisted Parsing**
  - Python parsers use regex + date parsing to extract assignments from PDFs and text.
  - Optional “AI Repair” mode uses Google Gemini to clean up messy dates and titles.

- **OCR for Screenshots**
  - Upload images of “Upcoming” widgets or Canvas screenshots.
  - Tesseract OCR converts the image to text, then the same parser extracts assignments.

- **Class-Based Organization**
  - Class “folders” with colors for each course.
  - Assignments are grouped by course and tagged with the right folder.

- **Calendar + Planner Views**
  - See what’s due **today**, **this week**, and **overdue** at a glance.
  - Calendar view for browsing assignments by date.

- **Progress Tracking**
  - Mark assignments as completed.
  - Quickly scan which tasks still need attention.

- **Auth & Personalization**
  - Users sign up and log in with Supabase Auth.
  - Row-level security ensures users only see their own data.
  - Simple onboarding walkthrough the first time someone logs in.

---
## How to use

### 1. Sign Up / Log In
Create an account or log in with your credentials.

### 2. Upload a Syllabus
- Tap the **+** button at the bottom
- Select **Upload Syllabus**
- Choose your method:
  - **Upload PDF** - Select a PDF file
  - **Upload Image** - Take a photo or select an image
  - **Paste Text** - Copy and paste syllabus text
- Toggle **AI Repair** for better date parsing
- Fill in class name, semester, year, and folder color
- Tap **Parse**

### 3. Review Assignments
- Review extracted assignments
- Edit titles, dates, or descriptions
- Delete any incorrect entries
- Tap **Save to Planner**

### 4. View Your Assignments
- **Home:** See today's assignments and quick stats
- **Classes:** Browse assignments by class
- **Calendar:** View assignments on specific dates
- **Profile:** Manage your account settings

---

## Known Limitations & Notes

- Some unusual syllabus formats may still confuse the parser, especially when dates are embedded in long paragraphs.
- Image OCR quality depends heavily on screenshot clarity (cropped Canvas “To Do” lists generally work best).
- The web version works best in incognito mode to avoid issues with cached auth sessions.

---

## Architecture Overview

Dueable is a small full-stack system with three main pieces:

1. **Frontend (React Native + Expo, exported to web)**  
   - Handles UI, navigation, file/image picking, and user flows.
   - Talks to the backend over HTTPS for parsing.
   - Reads and writes user data via Supabase.

2. **Backend (FastAPI on Render)**  
   - Provides endpoints for syllabus parsing:
     - `POST /assignments/pdf` – PDF upload + parsing
     - `POST /assignments/image` – image upload + OCR + parsing
     - `POST /assignments/text` – plain text parsing
   - Uses Python libraries (PyMuPDF, regex, dateparser, Tesseract) to extract assignment info.
   - Optionally calls the Gemini API to repair/normalize dates and titles.
   - Performs duplicate detection so the same syllabus is not imported twice.

3. **Database (Supabase / Postgres)**  
   - Stores users, class folders, assignments, and basic user settings.
   - Uses Supabase’s row-level security so each user only sees their own classes and assignments.
   - Exposed to the frontend through the Supabase client.

---

## Tech Stack

### Frontend

- **React Native + Expo**  
  Built the UI in React Native with Expo, but also exported it as a web app so it can run in the browser.
- **TypeScript**  
  Used for type safety across components, navigation, and context.
- **Expo Router**  
  File-based routing for screens like Home, Classes, Calendar, Login, and Signup.
- **Supabase Auth**  
  Log in / sign up, session handling, and protected routes.
- **React Context API**  
  `AssignmentsContext` stores assignments and class folders, shared across the app.

### Backend

- **Python**
- **FastAPI**  
  Defines the API endpoints for parsing syllabi and returning structured assignment data.
- **PyMuPDF (fitz)**  
  Extracts text from PDF syllabi page by page.
- **Regular Expressions + Custom Parsing Logic**  
  Finds patterns that look like assignments:
  - “Assignment 3 – Project Proposal – due Sept 10”
  - “Week 4 (Tue Sept 22) – Quiz 1”
- **Tesseract OCR (via pytesseract)**  
  Converts syllabus screenshots into text so they can go through the same parsing pipeline.
- **dateparser**  
  Turns fuzzy strings like “Tues (week of November 3)” into usable dates when possible.
- **Google Gemini API**  
  Optional repair step that tries to:
  - Clean noisy assignment titles.
  - Normalize and fix ambiguous dates.
  - Remove duplicates or clearly invalid rows.

### Database & Hosting

- **Supabase (Postgres)**  
  - Stores user accounts, assignments, class folders, and user settings.
  - Row-level security policies to protect each user’s data.
- **Backend Hosting: Render**  
  - FastAPI app is hosted at: `https://cs370pixelate.onrender.com`
  - Docker is used so dependencies like Tesseract and system libraries are installed the same way in development and production.
- **Frontend Hosting: Netlify**  
  - Expo web build is deployed to Netlify for easy sharing and access.

---

## ⚙️ Running the Project Locally (Optional)

- **Frontend (Expo / React Native Web)**  
cd pixelate
npm install
npx expo start --web

- The app should open in your browser (or at http://localhost:8081 depending on your Expo config).

- **Backend (FastAPI)**
bash
Copy code
cd syllabus-backend
pip install -r requirements.txt
uvicorn app.app:app --reload

- By default, this will run the API at http://127.0.0.1:8000.

Note: To use image OCR locally, you need Tesseract installed and available on your PATH
– for example on macOS: brew install tesseract.

You will also need a Supabase project and environment variables set up for the backend and frontend to talk to your own database if you’re not using the existing hosted services.

## Project Structure

### Frontend (`pixelate/`)

```
pixelate/
├── app/                          # Expo Router screens
│   ├── (protected)/             # Protected routes (require auth)
│   │   ├── home.tsx            # Main dashboard with today's assignments
│   │   ├── layout.tsx          # Bottom tab navigation wrapper
│   │   └── profile.tsx         # User profile and settings
│   ├── auth/
│   │   └── callback.tsx        # Supabase auth callback handler
│   ├── _layout.tsx             # Root layout with navigation + context
│   ├── calendar.tsx            # Calendar view (month/week/day)
│   ├── classes.tsx             # Class list with folder cards
│   ├── index.tsx               # Entry point / redirect
│   ├── login.tsx               # Login screen
│   └── signup.tsx              # Signup screen
│
├── components/                  # Reusable UI components
│   ├── AssignmentsContext.tsx  # Global state for assignments
│   ├── CalendarView.tsx        # Calendar UI component
│   ├── ClassList.tsx           # Class folder cards
│   ├── PlusMenu.tsx            # Floating + button menu
│   └── UploadSyllabusModal.tsx # Syllabus upload modal (PDF/text/image)
│
├── constant/                    # App constants and utilities
│   ├── api.ts                  # API base URL builder
│   ├── colors.ts               # Color palette
│   └── supabase.js             # Supabase client config
│
├── assets/                      # Images, fonts, icons
├── dist/                        # Built web app (generated)
├── .env                         # Environment variables
├── app.json                     # Expo configuration
├── package.json                 # Dependencies
└── tsconfig.json               # TypeScript configuration
```

### Backend (`syllabus-backend/`)

```
syllabus-backend/
├── app/
│   ├── __init__.py             # FastAPI app initialization & endpoints
│   ├── pdf_extractor.py        # PDF text extraction & assignment parsing
│   ├── llm_repair.py           # Gemini AI integration for date normalization
│   └── ocr/
│       └── ocr_processor.py    # Image OCR processing with Tesseract
├── requirements.txt            # Python dependencies
└── README.md                   # Backend-specific documentation
```

### Key Files Explained

**`app/_layout.tsx`**  
Root layout that wraps the entire app in `AssignmentsProvider` for global state. Renders bottom tab navigation (Home, Classes, Calendar, Profile) and the floating + button. Hides navigation on login/signup screens.

**`components/AssignmentsContext.tsx`**  
React Context that stores all assignments for the current user. Provides `useAssignments()` hook for reading/writing assignment data. Includes helper functions for date normalization, priority assignment, and duplicate detection.

**`components/UploadSyllabusModal.tsx`**  
Full-screen modal for uploading syllabi. Supports PDF upload, image upload (OCR), and pasted text. Includes AI Repair toggle for LLM-based date parsing. Sends files to backend endpoints (`/assignments/pdf`, `/assignments/image`, `/assignments/text`) and converts parsed results into draft assignments for review.

**`components/PlusMenu.tsx`**  
Floating action button menu that slides up to reveal options: Upload Syllabus, Add Class, Add Assignment. Triggers the upload flow modal.

**`app/(protected)/home.tsx`**  
Main dashboard displaying welcome message, stats (upcoming vs overdue), and today's assignments filtered by class. Primary landing page after login.

**`app/classes.tsx`**  
Displays all classes as color-coded folder cards showing overdue and upcoming assignment counts. Tapping a class shows all related assignments.

**`app/calendar.tsx`**  
Calendar interface with month/week/day toggle. Highlights dates with assignments and shows assignment details when a date is selected.

**`app/login.tsx` & `app/signup.tsx`**  
Authentication screens for email/password login and account creation. After successful auth, shows a brief app tutorial before navigating to the home screen.

**`constant/supabase.js`**  
Configures the Supabase client with custom storage adapter that uses SecureStore on mobile and localStorage on web, enabling cross-platform authentication.

---

### Backend Files Explained

**`app/__init__.py`**  
Main FastAPI application with three core endpoints:
- **POST `/assignments/pdf`** - Accepts PDF upload, extracts text with PyMuPDF, parses assignments using regex patterns, optionally repairs dates with Gemini AI, and detects duplicates via SHA-256 hash stored in Supabase
- **POST `/assignments/image`** - Accepts image upload, runs OCR with Tesseract to extract text, parses assignments, optional AI repair
- **POST `/assignments/text`** - Accepts plain text input for simple parsing without OCR or AI

Each endpoint returns structured JSON with assignment items containing: `title`, `due_date_raw`, `due_date_iso`, `due_mdy`, `due_time`, `assignment_type`, `course`, `page`, and `source`.

Includes CORS middleware for cross-origin requests, Supabase integration for duplicate detection and upload tracking, and comprehensive error handling with fallback to in-memory caching if database is unavailable.

**`app/pdf_extractor.py`**  
Core PDF and text parsing logic using PyMuPDF for PDF text extraction and regex patterns for assignment detection. Includes multiple parsing strategies:
- **Pass A:** Explicit "due/given ... date" patterns
- **Pass B:** Schedule rows starting with month-name dates
- **Pass C:** "due on <date>" patterns  
- **Pass D:** Week-based patterns (e.g., "Week 3 (Mon Jan 27)")
- **Pass E:** Weekday patterns (e.g., "due by Tuesday and Thursday")

Detects course names from first page, infers fallback year from semester mentions, normalizes dates to ISO format using `dateparser`, assigns assignment types (Quiz, Test, Presentation, Assignment), tracks which PDF page each assignment appears on, and deduplicates results based on title and date.

**`app/llm_repair.py`**  
Google Gemini AI integration for cleaning and normalizing parsed assignments. Sends full syllabus text + seed items from regex parser to Gemini with a system prompt instructing it to:
- Clean OCR noise from titles
- Remove duplicate assignments
- Fix obviously wrong dates using syllabus context
- Return only valid JSON with cleaned items

Falls back gracefully to original seed items if Gemini is not configured or errors occur. Uses `gemini-2.5-pro` model with configurable API key via environment variables.

**`app/ocr/ocr_processor.py`**  
Image-to-text processing using Tesseract OCR. Accepts syllabus screenshots/photos, preprocesses images with OpenCV (adaptive thresholding, noise reduction, contrast enhancement), extracts text with pytesseract, and parses assignments using the same regex patterns as PDF extraction. Supports multiple preprocessing methods optimized for different image types (screenshots vs photos).

---

## Contributors

**Team Pixelate**
- Kultum: Product Owner and Full-stack dev (parsers, FastAPI wiring, Supabase schema, frontend integration)
- Nyah: Scrum Master and frontend
- Kayla: OCR tuning and frontend work
- Taylor: UI and UX support
- Olivia: UI and testing

---

## License

This project was created for Emory CS370.

---

## Acknowledgments

- Built with [Expo](https://expo.dev/)
- Authentication by [Supabase](https://supabase.com/)
- Icons by [Lucide React Native](https://lucide.dev/)
- Backend hosted on [Render](https://render.com/)
- Web deployment by [Netlify](https://netlify.com/)