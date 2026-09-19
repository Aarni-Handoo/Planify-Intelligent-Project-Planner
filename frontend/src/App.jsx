import React, { useState, useEffect, useRef } from "react";
import { checkBackend } from "./services/api";
import HomePage from "./components/HomePage";
import SetupScreen from "./components/SetupScreen";
import PlannerScreen from "./components/PlannerScreen";
import AddTaskModal from "./components/AddTaskModal";
import ShiftModal from "./components/ShiftModal";
import { S } from "./styles";

import {
    today,
    addDays,
    diffDays,
    uid,
    generateCode,
    matchesKeywords,
    FRONTEND_KEYWORDS,
    BACKEND_KEYWORDS,
    DB_KEYWORDS,
    DESIGN_KEYWORDS,
    DEVOPS_KEYWORDS
} from "./utils/dateHelpers";


// ─── Storage helpers ──────────────────────────────────────────────────────────

const STORAGE_PREFIX = "planify_project_";


const saveProject = (code, data) =>
{
    try
    {
        localStorage.setItem(
            STORAGE_PREFIX + code,
            JSON.stringify({
                ...data,
                savedAt: Date.now()
            })
        );
    }
    catch (e)
    {
        console.warn("Storage save failed", e);
    }
};


const loadProject = (code) =>
{
    try
    {
        const raw = localStorage.getItem(
            STORAGE_PREFIX + code.trim().toUpperCase()
        );

        return raw ? JSON.parse(raw) : null;
    }
    catch
    {
        return null;
    }
};


// ─── Sub-components ──────────────────────────────────────────────────────────

function Spinner()
{
    return <span>⟳</span>;
}


function Toast({ msg, type })
{
    const colors =
    {
        error: "#ef4444",
        warn: "#f59e0b",
        success: "#10b981",
        info: "#6366f1"
    };

    return (
        <div
            style={{
                position: "fixed",
                bottom: 24,
                right: 24,
                zIndex: 9999,
                background: colors[type] || colors.info,
                color: "#fff",
                padding: "13px 18px",
                borderRadius: 12,
                fontSize: 13,
                fontWeight: 700,
                boxShadow: "0 8px 30px rgba(0,0,0,.18)",
                maxWidth: 380
            }}
        >
            {msg}
        </div>
    );
}


// ─── Main App ────────────────────────────────────────────────────────────────

export default function App()
{
    const [screen, setScreen] = useState("home");

    const [projectCode, setProjectCode] = useState("");

    const [project, setProject] = useState(
    {
        name: "",
        startDate: today(),
        deadline: "",
        description: "",
        notes: ""
    });

    const [members, setMembers] = useState(
    [
        {
            id: uid(),
            name: "",
            skills: ""
        }
    ]);

    const [tasks, setTasks] = useState([]);

    const [loading, setLoading] = useState(false);
    const [loadMsg, setLoadMsg] = useState("");

    const [notification, setNotification] = useState(null);

    const [shiftModal, setShiftModal] = useState(null);

    const [addModalOpen, setAddModalOpen] = useState(false);

    const [editingTask, setEditingTask] = useState(null);


    // ─── Set today's date ─────────────────────────────────────────────────────

    useEffect(() =>
    {
        setProject((prev) =>
        ({
            ...prev,
            startDate: today()
        }));
    }, []);

    useEffect(() => {

    checkBackend()
        .then((data) => {
            console.log("BACKEND RESPONSE:", data);
        })
        .catch((error) => {
            console.error("BACKEND ERROR:", error);
        });

}, []);
    // ─── Auto save ────────────────────────────────────────────────────────────

    const autoSaveRef = useRef(null);

    useEffect(() =>
    {
        if (screen !== "planner" || !projectCode)
        {
            return;
        }

        clearTimeout(autoSaveRef.current);

        autoSaveRef.current = setTimeout(() =>
        {
            saveProject(
                projectCode,
                {
                    project,
                    members,
                    tasks
                }
            );
        }, 800);

    }, [tasks, project, members, screen, projectCode]);


    // ─── Toast ────────────────────────────────────────────────────────────────

    const toast = (msg, type = "info") =>
    {
        setNotification({
            msg,
            type
        });

        setTimeout(() =>
        {
            setNotification(null);
        }, 4500);
    };


    // ─── Reminders ────────────────────────────────────────────────────────────

    useEffect(() =>
    {
        if (!tasks.length)
        {
            return;
        }

        const todayStr = today();

        tasks.forEach((t) =>
        {
            if (t.completed || t.deleted)
            {
                return;
            }

            const diff = diffDays(t.dueDate, todayStr);

            if (diff === 1)
            {
                toast(
                    `⚠ "${t.title}" is due TOMORROW!`,
                    "warn"
                );
            }

            if (diff === 0)
            {
                toast(
                    `🔴 "${t.title}" is due TODAY!`,
                    "error"
                );
            }

            if (diff < 0)
            {
                toast(
                    `⛔ "${t.title}" is OVERDUE!`,
                    "error"
                );
            }
        });

    }, [tasks.map(t => t.id).join()]);


    // ─── Create new project ──────────────────────────────────────────────────

    const startPlanner = async () =>
    {
        if (
            !project.name ||
            !project.startDate ||
            !project.deadline
        )
        {
            return toast(
                "Fill project name, start date & deadline",
                "error"
            );
        }

        if (members.some(m => !m.name))
        {
            return toast(
                "All members need a name",
                "error"
            );
        }

        setLoading(true);
        setLoadMsg("Creating your project space...");

        await new Promise((r) => setTimeout(r, 700));

        const code = generateCode();

        setProjectCode(code);

        setTasks([]);

        saveProject(
            code,
            {
                project,
                members,
                tasks: []
            }
        );

        setScreen("planner");

        setLoading(false);

        toast(
            `✅ Project created! Your code: ${code}`,
            "success"
        );
    };


    // ─── Join existing project ────────────────────────────────────────────────

    const joinProject = async (code) =>
    {
        setLoading(true);
        setLoadMsg("Looking up project...");

        await new Promise((r) => setTimeout(r, 600));

        const data = loadProject(code);

        if (!data)
        {
            setLoading(false);

            return toast(
                "❌ No project found with that code. Check and try again.",
                "error"
            );
        }

        setProject(data.project);

        setMembers(data.members);

        setTasks(data.tasks || []);

        setProjectCode(
            code.trim().toUpperCase()
        );

        setScreen("planner");

        setLoading(false);

        toast(
            `✅ Joined project: ${data.project.name}`,
            "success"
        );
    };


    // ─── Smart assignee ──────────────────────────────────────────────────────

    const getAssignees = (role) =>
    {
        const memberList = members.filter(m => m.name);

        if (!memberList.length || role === "team")
        {
            return ["Team"];
        }

        let matched = [];


        if (role === "frontend")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    FRONTEND_KEYWORDS
                ) &&
                !matchesKeywords(
                    m.skills,
                    BACKEND_KEYWORDS
                )
            );

            if (!matched.length)
            {
                matched = memberList.filter(m =>
                    matchesKeywords(
                        m.skills,
                        FRONTEND_KEYWORDS
                    )
                );
            }
        }


        else if (role === "backend")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    BACKEND_KEYWORDS
                ) &&
                !matchesKeywords(
                    m.skills,
                    FRONTEND_KEYWORDS
                )
            );

            if (!matched.length)
            {
                matched = memberList.filter(m =>
                    matchesKeywords(
                        m.skills,
                        BACKEND_KEYWORDS
                    )
                );
            }
        }


        else if (role === "database")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    DB_KEYWORDS
                )
            );

            if (!matched.length)
            {
                matched = memberList.filter(m =>
                    matchesKeywords(
                        m.skills,
                        BACKEND_KEYWORDS
                    )
                );
            }
        }


        else if (role === "design")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    DESIGN_KEYWORDS
                )
            );
        }


        else if (role === "devops")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    DEVOPS_KEYWORDS
                )
            );
        }


        else if (role === "fullstack")
        {
            matched = memberList.filter(m =>
                matchesKeywords(
                    m.skills,
                    FRONTEND_KEYWORDS
                ) ||
                matchesKeywords(
                    m.skills,
                    BACKEND_KEYWORDS
                )
            );
        }


        return matched.length
            ? matched.map(m => m.name)
            : ["Team"];
    };


    // ─── Suggest tasks ───────────────────────────────────────────────────────

    const recommendTasks = async () =>
    {
        setLoading(true);

        setLoadMsg("Building your task roadmap...");

        await new Promise((r) => setTimeout(r, 900));

        const start = project.startDate;
        const end = project.deadline;

        const totalDays = diffDays(end, start);


        const phases =
        [
            {
                title: "Project Kickoff Meeting",
                role: "team",
                pctStart: 0,
                pctEnd: 3,
                priority: "HIGH",
                desc: "Align the team on goals, scope, timeline, and key deliverables."
            },

            {
                title: "Requirements Gathering",
                role: "team",
                pctStart: 2,
                pctEnd: 10,
                priority: "HIGH",
                desc: "Collect user stories, business requirements, and define acceptance criteria."
            },

            {
                title: "UI/UX Wireframing",
                role: "design",
                pctStart: 10,
                pctEnd: 20,
                priority: "HIGH",
                desc: "Create low-fidelity wireframes and user flow diagrams."
            },

            {
                title: "Visual Design & Mockups",
                role: "design",
                pctStart: 18,
                pctEnd: 27,
                priority: "MEDIUM",
                desc: "Produce high-fidelity designs, colour palettes, and component styles."
            },

            {
                title: "Database Schema Design",
                role: "database",
                pctStart: 15,
                pctEnd: 23,
                priority: "HIGH",
                desc: "Define entity relationships, schema, indexes, and migration plan."
            },

            {
                title: "Backend Architecture & API Setup",
                role: "backend",
                pctStart: 20,
                pctEnd: 32,
                priority: "HIGH",
                desc: "Scaffold backend, configure auth, and define core REST/GraphQL endpoints."
            },

            {
                title: "Frontend Development – Phase 1",
                role: "frontend",
                pctStart: 28,
                pctEnd: 45,
                priority: "HIGH",
                desc: "Build core UI components, routing, and responsive layouts."
            },

            {
                title: "Backend Core Feature Development",
                role: "backend",
                pctStart: 32,
                pctEnd: 50,
                priority: "HIGH",
                desc: "Implement main business logic, controllers, services and middleware."
            },

            {
                title: "Database Integration",
                role: "database",
                pctStart: 38,
                pctEnd: 48,
                priority: "MEDIUM",
                desc: "Connect ORM/queries to backend services; implement CRUD operations."
            },

            {
                title: "Frontend–Backend Integration",
                role: "fullstack",
                pctStart: 50,
                pctEnd: 63,
                priority: "MEDIUM",
                desc: "Wire frontend components to live API endpoints, handle state and errors."
            },

            {
                title: "Stakeholder Review & Feedback",
                role: "team",
                pctStart: 63,
                pctEnd: 68,
                priority: "MEDIUM",
                desc: "Demo current build to stakeholders; collect feedback and prioritise changes."
            },

            {
                title: "Frontend Development – Phase 2",
                role: "frontend",
                pctStart: 68,
                pctEnd: 76,
                priority: "MEDIUM",
                desc: "Apply feedback, polish UI, add secondary features and accessibility."
            },

            {
                title: "Testing & QA",
                role: "fullstack",
                pctStart: 76,
                pctEnd: 86,
                priority: "HIGH",
                desc: "Write unit, integration, and E2E tests; fix bugs and edge cases."
            },

            {
                title: "Performance & Security Audit",
                role: "backend",
                pctStart: 85,
                pctEnd: 91,
                priority: "MEDIUM",
                desc: "Optimise load times, fix vulnerabilities, review OWASP checklist."
            },

            {
                title: "Final Review & Staging Deploy",
                role: "team",
                pctStart: 91,
                pctEnd: 96,
                priority: "HIGH",
                desc: "Full regression test on staging; sign-off from stakeholders."
            },

            {
                title: "Production Deployment",
                role: "devops",
                pctStart: 95,
                pctEnd: 98,
                priority: "HIGH",
                desc: "Release to production, monitor logs, configure alerts and rollback plan."
            },

            {
                title: "Documentation & Handover",
                role: "team",
                pctStart: 97,
                pctEnd: 100,
                priority: "LOW",
                desc: "Write user guides, API docs, internal wiki, and complete project handover."
            }
        ];


        const newTasks = phases.map((p) =>
        {
            const taskStart = addDays(
                start,
                Math.round(totalDays * p.pctStart / 100)
            );

            const taskDue = addDays(
                start,
                Math.min(
                    Math.round(totalDays * p.pctEnd / 100),
                    totalDays
                )
            );

            const dur = Math.max(
                1,
                diffDays(taskDue, taskStart) + 1
            );


            return {
                id: uid(),
                title: p.title,
                description: p.desc,
                assignees: getAssignees(p.role),
                priority: p.priority,
                durationDays: dur,
                startDate: taskStart,
                dueDate: taskDue,
                dependencies: [],
                completed: false,
                deleted: false
            };
        });


        setTasks((prev) =>
        [
            ...prev,
            ...newTasks
        ]);


        setLoading(false);

        toast(
            `✅ Added ${newTasks.length} tasks in logical sequence!`,
            "success"
        );
    };


    // ─── Task actions ────────────────────────────────────────────────────────

    const toggleComplete = (id) =>
    {
        setTasks((prev) =>
            prev.map((t) =>
                t.id === id
                    ? {
                        ...t,
                        completed: !t.completed
                    }
                    : t
            )
        );

        toast(
            "Task status updated",
            "success"
        );
    };


    const deleteTask = (id) =>
    {
        setTasks((prev) =>
            prev.map((t) =>
                t.id === id
                    ? {
                        ...t,
                        deleted: true
                    }
                    : t
            )
        );

        toast(
            "🗑 Task removed.",
            "info"
        );
    };


    // ─── Shift task ──────────────────────────────────────────────────────────

    const shiftTask = (taskId, newDate) =>
    {
        setTasks((prev) =>
        {
            const task = prev.find(
                t => t.id === taskId
            );

            if (!task)
            {
                return prev;
            }

            const delta = diffDays(
                newDate,
                task.dueDate
            );


            return prev.map((t) =>
            {
                if (t.id === taskId)
                {
                    return {
                        ...t,
                        dueDate: newDate
                    };
                }

                if (t.dependencies?.includes(taskId))
                {
                    return {
                        ...t,
                        dueDate: addDays(
                            t.dueDate,
                            delta
                        )
                    };
                }

                return t;
            });
        });


        setShiftModal(null);

        toast(
            "📅 Deadline shifted.",
            "success"
        );
    };


    // ─── Add/Edit task ───────────────────────────────────────────────────────

    const handleSaveTask = (taskData) =>
    {
        if (editingTask)
        {
            setTasks((prev) =>
                prev.map((t) =>
                    t.id === editingTask.id
                        ? {
                            ...t,
                            ...taskData,
                            dependencies: t.dependencies || []
                        }
                        : t
                )
            );

            toast(
                "✅ Task updated",
                "success"
            );
        }
        else
        {
            setTasks((prev) =>
            [
                ...prev,
                {
                    id: uid(),
                    ...taskData,
                    dependencies: [],
                    completed: false,
                    deleted: false
                }
            ]);

            toast(
                "✅ Task added",
                "success"
            );
        }


        setAddModalOpen(false);

        setEditingTask(null);
    };


    // ─── Reset project ───────────────────────────────────────────────────────

    const handleReset = () =>
    {
        setScreen("home");

        setTasks([]);

        setProjectCode("");

        setProject(
        {
            name: "",
            startDate: today(),
            deadline: "",
            description: "",
            notes: ""
        });

        setMembers(
        [
            {
                id: uid(),
                name: "",
                skills: ""
            }
        ]);
    };


    // ─── Delete entire project ───────────────────────────────────────────────

    const deleteProject = () =>
    {
        if (!projectCode)
        {
            return;
        }

        const confirmed = window.confirm(
            `🗑 Delete project "${project.name}" permanently?\n\nThis cannot be undone.`
        );

        if (!confirmed)
        {
            return;
        }


        try
        {
            localStorage.removeItem(
                STORAGE_PREFIX + projectCode
            );
        }
        catch (e)
        {
            console.warn("Project deletion failed", e);
        }


        setProjectCode("");

        setProject(
        {
            name: "",
            startDate: today(),
            deadline: "",
            description: "",
            notes: ""
        });

        setMembers(
        [
            {
                id: uid(),
                name: "",
                skills: ""
            }
        ]);

        setTasks([]);

        setScreen("home");

        toast(
            "🗑 Project deleted permanently.",
            "error"
        );
    };


    // ─── Derived values ──────────────────────────────────────────────────────

    const activeTasks = tasks.filter(
        t => !t.deleted
    );

    const done = activeTasks.filter(
        t => t.completed
    ).length;

    const pct = activeTasks.length
        ? Math.round(
            (done / activeTasks.length) * 100
        )
        : 0;


    const todayStr = today();


    const deadlinePct = (() =>
    {
        const onTime = activeTasks.filter(
            t =>
                t.completed &&
                t.dueDate >= todayStr
        ).length;

        const totalC = activeTasks.filter(
            t => t.completed
        ).length;

        return totalC
            ? Math.round(
                (onTime / totalC) * 100
            )
            : 100;
    })();

    useEffect(() => {

    checkBackend()
        .then((data) => {
            console.log("HEALTH:", data);
        });

    fetch("http://localhost:5000/api/analyze-task", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: "Build Login API",
            description: "Implement authentication using JWT",
            projectType: "Backend Heavy"
        })
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("ANALYZE TASK:", data);
        })
        .catch((error) => {
            console.error("ANALYZE ERROR:", error);
        });

}, []);




    


    // ─── Render ──────────────────────────────────────────────────────────────

    return (
        <div style={S.root}>

            {notification && (
                <Toast
                    msg={notification.msg}
                    type={notification.type}
                />
            )}


            {screen === "home" && (
                <HomePage
                    onNewProject={() =>
                    {
                        setScreen("setup");
                    }}

                    onJoinProject={joinProject}

                    loading={loading}

                    loadMsg={loadMsg}
                />
            )}


            {screen === "setup" && (
                <SetupScreen
                    project={project}
                    setProject={setProject}

                    members={members}
                    setMembers={setMembers}

                    onStart={startPlanner}

                    onBack={() =>
                    {
                        setScreen("home");
                    }}

                    loading={loading}
                    loadMsg={loadMsg}
                />
            )}


            {screen === "planner" && (
                <PlannerScreen
                    project={project}

                    tasks={activeTasks}

                    members={members}

                    pct={pct}

                    deadlinePct={deadlinePct}

                    projectCode={projectCode}

                    onToggleComplete={toggleComplete}

                    onDelete={deleteTask}

                    onShift={(id) =>
                    {
                        const t = activeTasks.find(
                            task => task.id === id
                        );

                        setShiftModal(
                        {
                            taskId: id,
                            newDate: t?.dueDate || today()
                        });
                    }}

                    onAddTask={() =>
                    {
                        setEditingTask(null);
                        setAddModalOpen(true);
                    }}

                    onEditTask={(t) =>
                    {
                        setEditingTask(t);
                        setAddModalOpen(true);
                    }}

                    onRecommend={recommendTasks}

                    onReset={handleReset}

                    onDeleteProject={deleteProject}

                    loading={loading}
                />
            )}


            {shiftModal && (
                <ShiftModal
                    task={
                        activeTasks.find(
                            t => t.id === shiftModal.taskId
                        )
                    }

                    onConfirm={(newDate) =>
                    {
                        shiftTask(
                            shiftModal.taskId,
                            newDate
                        );
                    }}

                    onClose={() =>
                    {
                        setShiftModal(null);
                    }}
                />
            )}


            {addModalOpen && (
                <AddTaskModal
                    taskToEdit={editingTask}

                    members={members}

                    projectDeadline={project.deadline}

                    onSave={handleSaveTask}

                    onClose={() =>
                    {
                        setAddModalOpen(false);
                        setEditingTask(null);
                    }}
                />
            )}

        </div>
    );
}