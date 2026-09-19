// ─── Date helpers ─────────────────────────────────────────────────────────────

// Uses local date parts to avoid UTC date shifting

export const today = () =>
{
    const d = new Date();

    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");

    return `${y}-${m}-${day}`;
};


export const addDays = (dateStr, days) =>
{
    const date = new Date(dateStr + "T12:00:00");

    date.setDate(date.getDate() + days);

    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");

    return `${y}-${m}-${d}`;
};


export const diffDays = (date1Str, date2Str) =>
{
    if (!date1Str || !date2Str)
    {
        return 0;
    }

    const d1 = new Date(date1Str + "T12:00:00");
    const d2 = new Date(date2Str + "T12:00:00");

    return Math.round(
        (d1.getTime() - d2.getTime()) /
        (1000 * 60 * 60 * 24)
    );
};


export const fmtDate = (dateStr) =>
{
    if (!dateStr)
    {
        return "";
    }

    return new Date(dateStr + "T12:00:00").toLocaleDateString(
        "en-US",
        {
            month: "short",
            day: "numeric"
        }
    );
};


// ─── ID helpers ──────────────────────────────────────────────────────────────

export const uid = () =>
{
    return (
        "id-" +
        Math.random().toString(36).substr(2, 9) +
        Date.now().toString(36)
    );
};


// ─── Project code generator ──────────────────────────────────────────────────

export const generateCode = () =>
{
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    const rand = (n) =>
    {
        return Array.from(
            { length: n },
            () => chars[Math.floor(Math.random() * chars.length)]
        ).join("");
    };

    return `${rand(3)}-${rand(4)}`;
};


// ─── Skill matching ──────────────────────────────────────────────────────────

export const matchesKeywords = (skills = "", keywords = []) =>
{
    if (!skills)
    {
        return false;
    }

    const s = skills.toLowerCase();

    return keywords.some((kw) => s.includes(kw));
};


// ─── Frontend skills ─────────────────────────────────────────────────────────

export const FRONTEND_KEYWORDS =
[
    "react",
    "vue",
    "angular",
    "nextjs",
    "next.js",
    "nuxt",
    "svelte",
    "html",
    "css",
    "scss",
    "sass",
    "tailwind",
    "javascript",
    "js",
    "typescript",
    "ts",
    "frontend",
    "front-end",
    "front end",
    "ui",
    "ux",
    "web"
];


// ─── Backend skills ──────────────────────────────────────────────────────────

export const BACKEND_KEYWORDS =
[
    "node",
    "nodejs",
    "express",
    "nestjs",
    "python",
    "django",
    "flask",
    "fastapi",
    "java",
    "spring",
    "springboot",
    "ruby",
    "rails",
    "php",
    "laravel",
    "go",
    "golang",
    "rust",
    "c#",
    "dotnet",
    ".net",
    "backend",
    "back-end",
    "back end",
    "api",
    "rest",
    "graphql",
    "server"
];


// ─── Database skills ─────────────────────────────────────────────────────────

export const DB_KEYWORDS =
[
    "sql",
    "mysql",
    "postgres",
    "postgresql",
    "mongodb",
    "mongo",
    "redis",
    "firebase",
    "supabase",
    "prisma",
    "orm",
    "cassandra",
    "dynamodb",
    "sqlite",
    "database",
    "db"
];


// ─── Design skills ───────────────────────────────────────────────────────────

export const DESIGN_KEYWORDS =
[
    "figma",
    "canva",
    "sketch",
    "xd",
    "adobe xd",
    "illustrator",
    "photoshop",
    "indesign",
    "ui",
    "ux",
    "design",
    "graphic",
    "wireframe",
    "mockup",
    "prototype",
    "visual",
    "animation",
    "motion",
    "branding"
];


// ─── DevOps skills ───────────────────────────────────────────────────────────

export const DEVOPS_KEYWORDS =
[
    "aws",
    "azure",
    "gcp",
    "cloud",
    "docker",
    "kubernetes",
    "k8s",
    "ci",
    "cd",
    "cicd",
    "jenkins",
    "github actions",
    "terraform",
    "nginx",
    "linux",
    "bash",
    "shell",
    "devops",
    "deploy",
    "infrastructure"
];


// ─── Priority colours ────────────────────────────────────────────────────────

export const priorityColor = (priority) =>
{
    if (priority === "HIGH")
    {
        return "#ef4444";
    }

    if (priority === "MEDIUM")
    {
        return "#f59e0b";
    }

    return "#10b981";
};


export const priorityBg = (priority) =>
{
    if (priority === "HIGH")
    {
        return "#fef2f2";
    }

    if (priority === "MEDIUM")
    {
        return "#fffbeb";
    }

    return "#f0fdf4";
};