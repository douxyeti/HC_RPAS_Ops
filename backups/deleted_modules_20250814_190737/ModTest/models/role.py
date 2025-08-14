class Role:
    def __init__(self, role_id, name, tasks=None):
        self.role_id = role_id
        self.name = name
        self.tasks = tasks or []

    def __str__(self):
        return f"Role(id={self.role_id}, name={self.name}, tasks_count={len(self.tasks)})"

    def to_dict(self):
        return {
            'id': self.role_id,
            'name': self.name,
            'tasks': [task.to_dict() if hasattr(task, 'to_dict') else task for task in self.tasks]
        }

    @staticmethod
    def from_dict(data):
        return Role(
            role_id=data.get('id'),
            name=data.get('name'),
            tasks=data.get('tasks', [])
        )
