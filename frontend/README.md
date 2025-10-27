# Vedic AI Astrology - Frontend

Next.js 14 frontend for AI-powered Vedic astrology service.

## Features

- Next.js 14 with App Router
- TypeScript
- Tailwind CSS + shadcn/ui
- React Query for data fetching
- Supabase authentication
- SVG birth chart visualization
- Responsive mobile design

## Setup

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

## Project Structure

```
app/
├── (auth)/              # Authentication pages
│   ├── login/
│   └── signup/
├── dashboard/           # Protected dashboard
│   ├── profiles/       # Profile management
│   ├── ask/            # Query interface
│   └── history/        # Query history
├── layout.tsx          # Root layout
└── page.tsx            # Landing page

components/
├── ui/                 # shadcn/ui components
├── chart/              # Chart visualizations
└── query/              # Query components

lib/
├── api.ts             # API client
├── supabase.ts        # Auth client
└── utils.ts           # Utilities
```

## Pages

- `/` - Landing page
- `/auth/login` - Login
- `/auth/signup` - Sign up
- `/dashboard` - Main dashboard
- `/dashboard/profiles` - Profile list
- `/dashboard/profiles/new` - Create profile
- `/dashboard/profiles/[id]` - View chart
- `/dashboard/ask` - Ask question
- `/dashboard/history` - Query history

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Set environment variables
4. Deploy

```bash
vercel --prod
```

### Docker

```bash
docker build -t vedic-astrology-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com \
  -e NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key \
  vedic-astrology-frontend
```

## License

MIT
