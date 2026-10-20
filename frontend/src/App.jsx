import React, { useState, useEffect, useRef } from "react";
import { checkBackend, planProject, recalculateSchedule } from "./services/api";
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
            skills: "",
            daily_capacity: 5
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

    // AI task decomposition + trained ML effort + capacity-aware scheduling.
    // Product users see only their project plan, never model internals.
    const mapScheduledTasks = (plan, startDate, prior = []) => {
        const allocations = plan.schedule_result?.assignments || [];
        const existing = new Map(prior.map(t => [t.id, t]));
        const memberNames = new Map(members.map(m => [String(m.id), m.name]));
        return plan.tasks.map(t => {
            const assigned = allocations.filter(a => a.task_id === t.id);
            const days = assigned.map(a => a.day);
            const first = days.length ? Math.min(...days) : null;
            const last = days.length ? Math.max(...days) : null;
            const assignees = [...new Set(assigned.map(a => a.member_name || memberNames.get(a.member_id)).filter(Boolean))];
            return {
                ...(existing.get(t.id) || {}),
                id: t.id, title: t.title, description: t.description || t.title,
                assignees: assignees.length ? assignees : ["Unassigned"],
                unscheduled: !days.length,
                unscheduledReason: plan.schedule_result?.unscheduled_tasks?.find(u => u.task_id === t.id)?.reason || "Not yet scheduled",
                priority: String(t.priority || "medium").toUpperCase(),
                startDate: first == null ? startDate : addDays(startDate, first - 1),
                dueDate: last == null ? startDate : addDays(startDate, last - 1),
                durationDays: last == null ? 0 : last - first + 1,
                dependencies: t.dependencies || [],
                required_skills: t.required_skills || [],
                estimated_hours: t.estimated_hours,
                complexity: t.complexity,
                category: t.category,
                completed: existing.get(t.id)?.completed || false,
                deleted: existing.get(t.id)?.deleted || false
            };
        });
    };

    const recommendTasks = async () => {
        setLoading(true);
        setLoadMsg("Creating your personalized project plan...");
        try {
            const days = Math.max(1, diffDays(project.deadline, project.startDate) + 1);
            const result = await planProject({
                project_name: project.name,
                description: project.description || "",
                project_type: "General",
                deadline_days: days,
                members: members.filter(m => m.name).map(m => ({
                    id: String(m.id), name: m.name, skills: m.skills,
                    daily_capacity: Number(m.daily_capacity ?? 5)
                }))
            });
            if (!result.success) throw new Error(result.error || "Planning failed");
            const mapped = mapScheduledTasks(result, project.startDate);
            lastReplan.current = mapped.map(t => `${t.id}:${!!t.completed}:${!!t.deleted}:${t.estimated_hours || 0}`).join("|");
            setTasks(mapped);
            const unscheduled = result.schedule_result.unscheduled_tasks || [];
            toast(unscheduled.length
                ? `Created ${mapped.length} tasks. ${unscheduled.length} need more time or matching skills.`
                : `Your personalized plan is ready: ${mapped.length} scheduled tasks!`,
                unscheduled.length ? "warn" : "success");
        } catch (error) {
            toast(`Unable to generate plan: ${error.message}`, "error");
        } finally {
            setLoading(false);
        }
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

        toast("Task status updated", "success");
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


    // Replan remaining work when task completion or deletion changes.
    const completionSignature = tasks.map(t => `${t.id}:${!!t.completed}:${!!t.deleted}:${t.estimated_hours || 0}`).join("|");
    const lastReplan = useRef("");
    useEffect(() => {
        if (screen !== "planner" || !tasks.length || !tasks.every(t => t.estimated_hours)) return;
        if (lastReplan.current === completionSignature) return;
        lastReplan.current = completionSignature;
        const remainingDays = Math.max(1, diffDays(project.deadline, today()) + 1);
        const remaining = tasks.filter(t => !t.deleted && !t.completed);
        if (!remaining.length) return;
        let cancelled = false;
        recalculateSchedule({
            deadline_days: remainingDays,
            members: members.filter(m => m.name).map(m => ({
                id: String(m.id), name: m.name, skills: m.skills,
                daily_capacity: Number(m.daily_capacity ?? 5)
            })),
            tasks: tasks.map(t => ({
                id: t.id, title: t.title, description: t.description,
                completed: t.completed, deleted: t.deleted,
                dependencies: t.dependencies || [],
                required_skills: t.required_skills || [],
                estimated_hours: t.estimated_hours,
                priority: (t.priority || "medium").toLowerCase()
            }))
        }).then(plan => {
            if (cancelled || !plan.success) return;
            const updated = mapScheduledTasks(plan, today(), tasks);
            const byId = new Map(updated.map(t => [t.id, t]));
            setTasks(prev => prev.map(t => t.completed || t.deleted ? t : (byId.get(t.id) || t)));
        }).catch(err => console.warn("Replanning unavailable", err));
        return () => { cancelled = true; };
    }, [completionSignature, screen]);

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
                skills: "",
            daily_capacity: 5
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
                skills: "",
            daily_capacity: 5
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