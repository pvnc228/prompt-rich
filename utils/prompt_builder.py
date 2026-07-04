import os
class PromptBuilder:
    def __init__(self, templates_dir: str = "config/prompts"):
        self.templates_dir=templates_dir
        if not os.path.exists(self.templates_dir):
            os.makedirs(templates_dir, exist_ok=False)
    def load_template(self, template_name: str) -> str:
        file_path = os.path.join(self.templates_dir, f"{template_name}.txt")
        if file_path:
            file = open(file_path, "r", encoding="utf-8")
            content = file.read()
            file.close()
            return content
        else:
            raise Exception
    def build(self, template_name: str, **variables) -> str:
        template = self.load_template(template_name)
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template
    def list_templates(self) -> list[str]:
        list = os.listdir(self.templates_dir)
        for items in list:
            if items.endswith(".txt"):
                [f[:-4] for f in list if f.endswith(".txt")]
        return list
