"""Planify Phase 5: collaborative, capacity-aware greedy scheduling.

Task estimated_hours represents TOTAL person-hours, not elapsed wall-clock hours.
Dependency tasks must complete on a prior day. Scheduling is heuristic, not optimal.
"""
from itertools import combinations
from math import isfinite
from .intelligence import normalize_skill
from .skill_ml import compatible
from .semantic import matches as semantic_matches

PRIORITY = {"high": 3, "medium": 2, "low": 1}
EPS = 1e-7
MIN_CONTRIBUTION = 0.25  # hours, for a contributor to count toward skill coverage


def _number(value, label, allow_zero=False):
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a number")
    try:
        n = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{label} must be a number")
    if not isfinite(n) or n < 0 or (not allow_zero and n <= 0):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'}")
    return n


# Narrow, auditable capability implications: knowledge of a language/tool
# includes routine operations with it, not unrelated specialist expertise.
CAPABILITIES = {
    "javascript": {"dom manipulation", "dom", "array methods", "web storage", "storage", "debugging"},
    "typescript": {"javascript", "dom manipulation", "dom", "array methods", "web storage", "storage", "debugging"},
    "css": {"responsive design"},
    "react": {"dom manipulation", "dom", "array methods"},
}

def _skills(value):
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
        raise ValueError("Skills must be a list of strings")
    direct = {normalize_skill(s)["canonical"] for s in value if s.strip()}
    return direct


def _deps(value):
    if value is None or value == "none":
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise ValueError("dependencies must be a list")
    return [str(x) for x in value]


def _match(task, member_id, member, required):
    decisions = task.get("eligibility", {})
    key = (str(member_id), str(required).lower())
    if key in decisions:
        # Auditable routine equivalences protect against over-literal LLM answers.
        # Do not invent specialist skills beyond semantic.py implications.
        return bool(decisions[key])
    return semantic_matches(required, member["skills"]) or compatible(required, member["skills"])["match"]


def _team_for_task(task, members, free, day, max_team_size):
    """Small-team set cover, preferring continuity and low lifetime utilization.

    Returns a team with enough remaining capacity for a meaningful contribution
    from every member. A team is only valid if its combined skills cover the task.
    """
    required = [] if task["preferred"] else task["skills"]
    candidates = [mid for mid, m in members.items()
                  if (not task["preferred"] or mid in task["preferred"]) and free[mid] >= min(MIN_CONTRIBUTION, task["remaining"]) - EPS and
                  (not required or any(_match(task,mid,m,r) for r in required))]
    if not candidates:
        return None
    # Exhaustive combinations for small teams; bounded search for larger groups.
    # Restrict to up to 14 candidates to avoid combinatorial explosion.
    candidates.sort(key=lambda mid: (
        0 if mid in task["preferred"] else 1,
        0 if mid in task["contributors"] else 1,
        members[mid]["total"] / members[mid]["capacity"],
        -free[mid], mid))
    candidates = candidates[:14]
    max_size = min(max_team_size, len(candidates))
    best = None
    best_score = None
    for size in range(1, max_size + 1):
        for combo in combinations(candidates, size):
            if not all(any(_match(task,mid,members[mid],r) for mid in combo) for r in required):
                continue
            # Every selected member must actually contribute to the task.
            if task["remaining"] + EPS < size * min(MIN_CONTRIBUTION, task["remaining"]):
                continue
            capacity = sum(free[mid] for mid in combo)
            can_finish_today = capacity + EPS >= task["remaining"]
            # Prefer finishing a task today if feasible; otherwise maximize
            # progress. Among finishing teams, prefer fewer contributors.
            score = (0 if task["preferred"] and set(combo).intersection(task["preferred"]) else 1,
                     0 if can_finish_today else 1,
                     size if can_finish_today else -capacity,
                     sum(mid not in task["contributors"] for mid in combo),
                     sum(members[mid]["total"] / members[mid]["capacity"] for mid in combo),
                     combo)
            if best_score is None or score < best_score:
                best, best_score = list(combo), score
    return best


def _allocate(task, team, members, free, day, assignments):
    """Allocate person-hours while counting every member's hours globally."""
    # First give every contributor a real amount of work, so coverage isn't fictitious.
    amounts = {mid: 0.0 for mid in team}
    for mid in team:
        give = min(MIN_CONTRIBUTION, free[mid], task["remaining"])
        amounts[mid] += give
        task["remaining"] -= give
    # Remaining hours are distributed in quarter-hour chunks to the member with
    # the lowest current-day utilization, with lifetime utilization as a tiebreak.
    while task["remaining"] > EPS:
        eligible = [mid for mid in team if free[mid] - amounts[mid] > EPS]
        if not eligible:
            break
        mid = min(eligible, key=lambda k: (
            (members[k]["capacity"] - free[k] + amounts[k]) / members[k]["capacity"],
            (members[k]["total"] + amounts[k]) / members[k]["capacity"], k))
        give = min(0.25, task["remaining"], free[mid] - amounts[mid])
        if give <= EPS:
            break
        amounts[mid] += give
        task["remaining"] -= give
    for mid, amount in amounts.items():
        if amount <= EPS:
            continue
        free[mid] = max(0.0, free[mid] - amount)
        members[mid]["total"] += amount
        task["contributors"].add(mid)
        assignments.append({
            "day": day, "task_id": task["id"], "task_title": task["title"],
            "member_id": mid, "member_name": members[mid]["name"],
            "hours": round(amount, 2),
            "contributed_skills": sorted(r for r in task["skills"] if _match(task,mid,members[mid],r))
        })
    task["remaining"] = max(0.0, task["remaining"])
    if task["remaining"] <= EPS:
        task["done_day"] = day


def build_schedule(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    raw_tasks = payload.get("tasks")
    raw_members = payload.get("members")
    if not isinstance(raw_tasks, list) or not isinstance(raw_members, list):
        raise ValueError("tasks and members must be lists")
    days = _number(payload.get("deadline_days", payload.get("deadlineDays")), "deadline_days")
    if not days.is_integer() or days > 365:
        raise ValueError("deadline_days must be an integer from 1 to 365")
    days = int(days)
    max_team_size = payload.get("max_team_size", 4)
    max_team_size = _number(max_team_size, "max_team_size")
    if not max_team_size.is_integer() or max_team_size > 8:
        raise ValueError("max_team_size must be an integer from 1 to 8")
    max_team_size = int(max_team_size)

    tasks = {}
    for t in raw_tasks:
        if not isinstance(t, dict):
            raise ValueError("Each task must be an object")
        tid = str(t.get("id", "")).strip()
        if not tid or tid in tasks:
            raise ValueError("Task IDs must be nonempty and unique")
        hours = _number(t.get("estimated_hours", t.get("estimatedHours")), f"Task {tid} estimated_hours")
        priority = str(t.get("priority", "medium")).lower()
        if priority not in PRIORITY:
            raise ValueError(f"Invalid priority for task {tid}")
        tasks[tid] = {
            "id": tid, "title": str(t.get("title", tid)),
            "skills": _skills(t.get("required_skills", t.get("skills", []))),
            "hours": hours, "remaining": hours, "priority": priority,
            "eligibility": {(str(mid), str(skill).lower()): bool(v)
                            for mid, choices in t.get("skill_eligibility", {}).items()
                            for skill, v in choices.items()},
            "deps": _deps(t.get("dependencies", t.get("dependency", []))),
            "preferred": set(map(str,t.get("preferred_member_ids",[]))),
            "done_day": None, "contributors": set()
        }
    for task in tasks.values():
        if len(task["deps"]) != len(set(task["deps"])):
            raise ValueError(f"Duplicate dependencies for task {task['id']}")
        for dep in task["deps"]:
            if dep not in tasks or dep == task["id"]:
                raise ValueError(f"Invalid dependency {dep} for task {task['id']}")
    states = {}
    def visit(tid):
        if states.get(tid) == 1:
            raise ValueError("Circular task dependencies detected")
        if states.get(tid) == 2:
            return
        states[tid] = 1
        for dep in tasks[tid]["deps"]:
            visit(dep)
        states[tid] = 2
    for tid in tasks:
        visit(tid)

    members = {}
    for m in raw_members:
        if not isinstance(m, dict):
            raise ValueError("Each member must be an object")
        mid = str(m.get("id", "")).strip()
        if not mid or mid in members:
            raise ValueError("Member IDs must be nonempty and unique")
        members[mid] = {
            "id": mid, "name": str(m.get("name", mid)),
            "skills": _skills(m.get("skills", [])),
            "capacity": _number(m.get("daily_capacity", m.get("dailyCapacity", 8)), f"Member {mid} daily_capacity"),
            "total": 0.0
        }
    # Prioritize tasks on the longest remaining dependency path, avoiding
    # the old greedy priority inversion that starved prerequisite chains.
    downstream = {tid: set() for tid in tasks}
    for tid, task in tasks.items():
        for dep in task['deps']:
            downstream[dep].add(tid)
    from functools import lru_cache
    @lru_cache(None)
    def critical(tid):
        return tasks[tid]['hours'] + max((critical(n) for n in downstream[tid]), default=0)
    assignments = []
    for day in range(1, days + 1):
        free = {mid: m["capacity"] for mid, m in members.items()}
        eligible = [t for t in tasks.values() if t["remaining"] > EPS and
                    all(tasks[dep]["done_day"] is not None and
                        tasks[dep]["done_day"] < day for dep in t["deps"])]
        eligible.sort(key=lambda t: (-critical(t["id"]), -PRIORITY[t["priority"]], t["id"]))
        # Multiple rounds let teams share capacity across tasks. Each task gets
        # one allocation per day, potentially across several collaborators.
        for task in eligible:
            team = _team_for_task(task, members, free, day, max_team_size)
            if team is not None:
                _allocate(task, team, members, free, day, assignments)

    unscheduled = []
    for t in tasks.values():
        if t["remaining"] <= EPS:
            continue
        missing=set() if t["preferred"] else {r for r in t["skills"] if not any(_match(t,mid,m,r) for mid,m in members.items())}
        if missing:
            reason = "Team is missing or must confirm required skills: " + ", ".join(sorted(missing))
        elif any(tasks[d]["done_day"] is None for d in t["deps"]):
            reason = "Dependency not completed within project deadline"
        else:
            reason = "Insufficient available days, team coverage or member capacity"
        unscheduled.append({"task_id": t["id"], "remaining_hours": round(t["remaining"], 2), "reason": reason})
    daily = [{"day": day, "assignments": [a for a in assignments if a["day"] == day]}
             for day in range(1, days + 1)]
    member_workload = []
    for mid, m in members.items():
        per_day = {str(day): round(sum(a["hours"] for a in assignments if a["day"] == day and a["member_id"] == mid), 2)
                   for day in range(1, days + 1)}
        member_workload.append({"member_id": mid, "name": m["name"], "total_hours": round(m["total"], 2),
                                "daily_capacity": m["capacity"], "daily_hours": per_day,
                                "utilization": round(m["total"] / (m["capacity"] * days), 4)})
    return {
        "success": True, "algorithm": "critical_path_capacity_aware_v3",
        "deadline_days": days, "schedule": daily, "assignments": assignments,
        "completed_tasks": [tid for tid, t in tasks.items() if t["done_day"] is not None],
        "unscheduled_tasks": unscheduled, "all_tasks_scheduled": not unscheduled,
        "member_workload": member_workload,
        "task_teams": [{"task_id": tid, "contributors": sorted(t["contributors"]),
                        "remaining_hours": round(t["remaining"], 2)} for tid, t in tasks.items()]
    }
