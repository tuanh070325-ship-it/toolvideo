# Video Tool Frontend

Modern workflow-based UI for AI-powered video processing.

## Features

- ✅ **White Theme Design** - Clean, professional interface
- ✅ **Square Buttons** - Simple, no rounded corners
- ✅ **Gray Dividers** - Light gray separators (#e5e7eb)
- ✅ **Shared Components** - Reusable, well-organized
- ✅ **Workflow Editor** - Node-based visual workflow building
- ✅ **TypeScript** - Full type safety
- ✅ **Responsive** - Works on all devices

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **ReactFlow** - Workflow editor
- **Zustand** - State management
- **TanStack Query** - API data fetching
- **Axios** - HTTP client

## Project Structure

```
frontend/
├── app/                    # Next.js app router
│   ├── page.tsx           # Dashboard
│   ├── workflows/         # Workflows pages
│   ├── videos/            # Videos page
│   └── generation/        # AI generation page
├── components/
│   ├── shared/            # SHARED COMPONENTS
│   │   ├── Button.tsx     # Reusable button
│   │   ├── Input.tsx      # Reusable input
│   │   ├── Card.tsx       # Reusable card
│   │   └── Navigation.tsx # Navigation bar
│   └── workflow/          # Workflow components
│       └── WorkflowCanvas.tsx
├── lib/
│   ├── api/               # API client
│   │   └── client.ts      # Backend API calls
│   ├── types/             # TypeScript types
│   │   └── api.ts         # API types
│   └── utils.ts           # Utility functions
└── package.json

```

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Pages

### Dashboard (`/`)
- Overview statistics
- Quick actions
- Recent activity

### Workflows (`/workflows`)
- List all workflows
- Create new workflows
- Manage templates

### Workflow Editor (`/workflows/editor`)
- Visual node-based editor
- Drag-and-drop nodes
- Connect nodes to build workflows

### Videos (`/videos`)
- Download videos from URLs
- Manage video library
- View processing status

### AI Generation (`/generation`)
- Text-to-video generation
- Image-to-video animation
- Generation history

## Shared Components

All shared components are in `components/shared/` and can be imported easily:

```tsx
import { Button, Input, Card, Navigation } from '@/components/shared'
```

### Button

```tsx
<Button>Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button size="sm">Small</Button>
```

### Input

```tsx
<Input placeholder="Enter text..." />
<Input type="number" />
```

### Card

```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
</Card>
```

## API Integration

The API client is fully typed and ready to use:

```tsx
import { videoAPI, workflowAPI, generationAPI } from '@/lib/api/client'

// Download video
const video = await videoAPI.download('https://...')

// List workflows
const { workflows } = await workflowAPI.list()

// Generate AI video
const result = await generationAPI.textToVideo({
  prompt: 'A cat playing',
  num_frames: 121
})
```

## Design Guidelines

### Colors
- Background: `#ffffff` (white)
- Text: `#111827` (gray-900)
- Border: `#e5e7eb` (gray-200)
- Muted: `#f9fafb` (gray-50)

### Spacing
- Use Tailwind spacing: `p-4`, `m-8`, `gap-6`
- Consistent padding in cards: `p-6`

### Borders
- All borders: `border border-gray-200`
- No rounded corners (square design)
- Dividers: `border-t border-gray-200`

## Development Tips

1. **Shared Components**: Always use shared components from `@/components/shared`
2. **TypeScript**: All API calls are fully typed
3. **Styling**: Use Tailwind classes, avoid custom CSS
4. **State**: Use Zustand for global state
5. **API Calls**: Use TanStack Query for data fetching

## License

MIT
