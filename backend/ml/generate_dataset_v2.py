import os
import random
import pandas as pd
from sklearn.model_selection import train_test_split

random.seed(42)

DATA_PATH = "../data/raw/Task_Categories.csv"
OUTPUT_DIR = "../data/processed"

NUMBER_OF_PROJECTS = 500


PROJECT_CONFIG = {
    "E-Commerce": [
        "frontend", "backend", "database",
        "ui/ux design", "testing", "devops", "cloud"
    ],
    "Social Media": [
        "frontend", "backend", "database",
        "ui/ux design", "ai/ml", "testing", "cloud"
    ],
    "Healthcare": [
        "frontend", "backend", "database",
        "data science", "ai/ml", "testing", "cloud"
    ],
    "Education": [
        "frontend", "backend", "database",
        "ui/ux design", "testing"
    ],
    "Banking": [
        "frontend", "backend", "database",
        "testing", "devops", "cloud"
    ],
    "Food Delivery": [
        "frontend", "backend", "database",
        "ui/ux design", "testing", "cloud"
    ],
    "Project Management": [
        "frontend", "backend", "database",
        "ui/ux design", "testing", "devops"
    ],
    "Booking System": [
        "frontend", "backend", "database",
        "ui/ux design", "testing", "cloud"
    ],
    "Inventory Management": [
        "frontend", "backend", "database",
        "data science", "testing"
    ],
    "Portfolio Website": [
        "frontend", "ui/ux design",
        "testing", "cloud"
    ]
}


DEPENDENCY_RULES = {
    "frontend": ["ui/ux design", "backend"],
    "backend": ["database", "cloud"],
    "testing": ["frontend", "backend", "ai/ml"],
    "devops": ["backend", "frontend", "testing"],
    "cloud": ["backend", "devops"],
    "ai/ml": ["data science"],
    "data science": ["database"]
}


CATEGORY_COMPLEXITY = {
    "frontend": 2,
    "backend": 3,
    "database": 3,
    "ui/ux design": 2,
    "testing": 2,
    "devops": 4,
    "cloud": 4,
    "ai/ml": 4,
    "data science": 3
}

COMPLEX_KEYWORDS = {
    "authentication": 1,
    "authorization": 1,
    "security": 1,
    "secure": 1,
    "payment": 1,
    "transaction": 1,
    "integration": 1,
    "optimization": 1,
    "distributed": 2,
    "microservice": 1,
    "machine learning": 1,
    "deep learning": 2,
    "classification": 1,
    "prediction": 1,
    "real-time": 1,
    "architecture": 1,
    "migration": 1
}

SIMPLE_KEYWORDS = {
    "button": -1,
    "color": -1,
    "logo": -1,
    "text": -1,
    "icon": -1,
    "basic": -1,
    "simple": -1
}


def calculate_complexity(description, category, skill_count):
    description = description.lower()

    score = CATEGORY_COMPLEXITY.get(category, 3)

    for keyword, weight in COMPLEX_KEYWORDS.items():
        if keyword in description:
            score += weight

    for keyword, weight in SIMPLE_KEYWORDS.items():
        if keyword in description:
            score += weight

    if skill_count >= 3:
        score += 1

    # Controlled noise
    score += random.choices(
        [-1, 0, 1],
        weights=[15, 70, 15]
    )[0]

    return max(1, min(5, score))



CATEGORY_EFFORT = {
    "frontend": 1.0,
    "backend": 1.3,
    "database": 1.2,
    "ui/ux design": 0.8,
    "testing": 0.9,
    "devops": 1.4,
    "cloud": 1.4,
    "ai/ml": 1.6,
    "data science": 1.3
}


def calculate_estimated_hours(complexity, category, skill_count):
    base_hours = complexity * 3

    category_factor = CATEGORY_EFFORT.get(category, 1.0)

    skill_factor = 1 + (skill_count - 1) * 0.08

    noise = random.uniform(0.85, 1.15)

    hours = (
        base_hours
        * category_factor
        * skill_factor
        * noise
    )

    return round(max(1, hours), 1)


CATEGORY_EFFORT = {
    "frontend": 1.0,
    "backend": 1.3,
    "database": 1.2,
    "ui/ux design": 0.8,
    "testing": 0.9,
    "devops": 1.4,
    "cloud": 1.4,
    "ai/ml": 1.6,
    "data science": 1.3
}


def calculate_estimated_hours(complexity, category, skill_count):
    base_hours = complexity * 3

    category_factor = CATEGORY_EFFORT.get(category, 1.0)

    skill_factor = 1 + (skill_count - 1) * 0.08

    noise = random.uniform(0.85, 1.15)

    hours = (
        base_hours
        * category_factor
        * skill_factor
        * noise
    )

    return round(max(1, hours), 1)



PROJECT_PRIORITY = {
    "E-Commerce": ["backend", "database", "frontend"],
    "Social Media": ["frontend", "backend", "ai/ml"],
    "Healthcare": ["backend", "ai/ml", "data science"],
    "Education": ["frontend", "backend", "database"],
    "Banking": ["backend", "database", "testing"],
    "Food Delivery": ["backend", "database", "frontend"],
    "Project Management": ["backend", "frontend", "database"],
    "Booking System": ["backend", "database", "frontend"],
    "Inventory Management": ["database", "backend", "data science"],
    "Portfolio Website": ["frontend", "ui/ux design", "testing"]
}


def calculate_priority(
    project_type,
    category,
    complexity,
    dependency
):
    score = 0

    if category in PROJECT_PRIORITY.get(project_type, []):
        score += 2

    if complexity >= 4:
        score += 2
    elif complexity == 3:
        score += 1

    if dependency != "none":
        score += 1

    score += random.choices(
        [-1, 0, 1],
        weights=[10, 80, 10]
    )[0]

    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"



def calculate_deadline(estimated_hours, complexity, team_size):
    daily_hours = 5

    expected_days = estimated_hours / daily_hours

    # Smaller teams receive slightly more time
    team_factor = 1.15 if team_size <= 3 else 1.0

    deadline = expected_days * team_factor

    deadline *= random.uniform(0.8, 1.5)

    return max(1, round(deadline))



def calculate_actual_hours(
    estimated_hours,
    complexity,
    team_size,
    dependency
):
    variation = random.gauss(0, 0.12)

    complexity_factor = 1 + (complexity - 3) * 0.04

    team_factor = 1.08 if team_size <= 3 else 1.0

    dependency_factor = 1.08 if dependency != "none" else 1.0

    actual_hours = (
        estimated_hours
        * (1 + variation)
        * complexity_factor
        * team_factor
        * dependency_factor
    )

    return round(max(1, actual_hours), 1)



def calculate_delay_hours(
    estimated_hours,
    actual_hours,
    deadline_days
):
    available_hours = deadline_days * 5

    # Delay means exceeding the available time,
    # not merely exceeding the original estimate.
    delay_hours = max(
        0,
        actual_hours - available_hours
    )

    return round(delay_hours, 1)



# ==========================================
# STEP 5: GENERATE DATASET V2
# ==========================================

def generate_dataset():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.join(
        base_dir, "..", "data", "raw", "Task_Categories.csv"
    )

    output_dir = os.path.join(
        base_dir, "..", "data", "processed"
    )

    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------
    # LOAD AND CLEAN KAGGLE DATA
    # --------------------------------------

    df = pd.read_csv(data_path)

    df = df.dropna(
        subset=["Task Description", "Category", "Skill"]
    ).copy()

    for column in ["Task Description", "Category", "Skill"]:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    df = df[
        (df["Task Description"] != "") &
        (df["Category"] != "") &
        (df["Skill"] != "")
    ].drop_duplicates()

    tasks = (
        df.groupby(["Task Description", "Category"])["Skill"]
        .apply(lambda values: sorted(set(values)))
        .reset_index()
    )

    tasks.columns = [
        "task_description",
        "category",
        "required_skills"
    ]

    # --------------------------------------
    # GENERATE PROJECTS
    # --------------------------------------

    generated_rows = []

    for project_id in range(1, NUMBER_OF_PROJECTS + 1):

        project_type = random.choice(
            list(PROJECT_CONFIG.keys())
        )

        project_categories = PROJECT_CONFIG[project_type]

        team_size = random.randint(2, 8)

        number_of_tasks = random.randint(8, 20)

        project_tasks = tasks[
            tasks["category"].isin(project_categories)
        ]

        selected_tasks = project_tasks.sample(
            n=min(number_of_tasks, len(project_tasks)),
            replace=False,
            random_state=random.randint(0, 1000000)
        )

        previous_tasks = []

        for _, task in selected_tasks.iterrows():

            description = task["task_description"]
            category = task["category"]

            # ----------------------------------
            # SELECT REQUIRED SKILLS
            # ----------------------------------

            available_skills = task["required_skills"]

            skill_count = random.randint(
                1,
                min(4, len(available_skills))
            )

            selected_skills = random.sample(
                available_skills,
                skill_count
            )

            # ----------------------------------
            # DEPENDENCIES
            # ----------------------------------

            dependency_categories = DEPENDENCY_RULES.get(
                category, []
            )

            possible_dependencies = [
                old_task["task_description"]
                for old_task in previous_tasks
                if old_task["category"] in dependency_categories
            ]

            if possible_dependencies and random.random() < 0.60:
                dependency = random.choice(
                    possible_dependencies
                )
            else:
                dependency = "none"

            # ----------------------------------
            # INTELLIGENT COMPLEXITY
            # ----------------------------------

            complexity = calculate_complexity(
                description,
                category,
                skill_count
            )

            # ----------------------------------
            # ESTIMATED HOURS
            # ----------------------------------

            estimated_hours = calculate_estimated_hours(
                complexity,
                category,
                skill_count
            )

            # ----------------------------------
            # PROJECT-AWARE PRIORITY
            # ----------------------------------

            priority = calculate_priority(
                project_type,
                category,
                complexity,
                dependency
            )

            # ----------------------------------
            # DEADLINE
            # ----------------------------------

            deadline_days = calculate_deadline(
                estimated_hours,
                complexity,
                team_size
            )

            # ----------------------------------
            # ACTUAL HOURS
            # ----------------------------------

            actual_hours = calculate_actual_hours(
                estimated_hours,
                complexity,
                team_size,
                dependency
            )

            # ----------------------------------
            # DELAY
            # ----------------------------------

            delay_hours = calculate_delay_hours(
                estimated_hours,
                actual_hours,
                deadline_days
            )

            # ----------------------------------
            # SAVE TASK RECORD
            # ----------------------------------

            generated_rows.append({
                "project_id": project_id,
                "project_type": project_type,
                "task_description": description,
                "category": category,
                "required_skills": ",".join(selected_skills),
                "skill_count": skill_count,
                "complexity": complexity,
                "priority": priority,
                "estimated_hours": estimated_hours,
                "actual_hours": actual_hours,
                "deadline_days": deadline_days,
                "team_size": team_size,
                "dependency": dependency,
                "delay_hours": delay_hours
            })

            previous_tasks.append({
                "task_description": description,
                "category": category
            })

    # --------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------

    planify_df = pd.DataFrame(generated_rows)

    print("Dataset V2 generated successfully!")
    print("Shape:", planify_df.shape)
    print("Projects:", planify_df["project_id"].nunique())

    # --------------------------------------
    # PROJECT-WISE SPLIT
    # --------------------------------------

    project_ids = planify_df["project_id"].unique()

    train_projects, temp_projects = train_test_split(
        project_ids,
        test_size=0.30,
        random_state=42
    )

    validation_projects, test_projects = train_test_split(
        temp_projects,
        test_size=0.50,
        random_state=42
    )

    train_df = planify_df[
        planify_df["project_id"].isin(train_projects)
    ].copy()

    validation_df = planify_df[
        planify_df["project_id"].isin(validation_projects)
    ].copy()

    test_df = planify_df[
        planify_df["project_id"].isin(test_projects)
    ].copy()

    # --------------------------------------
    # SAVE V2 FILES
    # --------------------------------------

    datasets = {
        "planify_dataset_v2.csv": planify_df,
        "train_v2.csv": train_df,
        "validation_v2.csv": validation_df,
        "test_v2.csv": test_df
    }

    for filename, dataset in datasets.items():

        path = os.path.join(output_dir, filename)

        dataset.to_csv(path, index=False)

        print("Saved:", filename, "Rows:", len(dataset))

    print("\nComplexity distribution:")
    print(planify_df["complexity"].value_counts().sort_index())

    print("\nPriority distribution:")
    print(planify_df["priority"].value_counts())

    print("\nDelay distribution:")
    print((planify_df["delay_hours"] > 0).value_counts())

    print("\nV2 DATASET GENERATION COMPLETE!")


if __name__ == "__main__":
    generate_dataset()


