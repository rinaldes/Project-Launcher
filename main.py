from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess

class Launcher(Extension):
  def __init__(self):
    super().__init__()
    self.subscribe(KeywordQueryEvent, ProjectFinder())

class ProjectFinder(EventListener):
  def on_event(self, event, ext):
    cmd = f"find {ext.preferences["folder"]} -type d -name .git -prune -exec dirname {{}} \;"

    if event.get_argument():
      cmd += f" | grep {event.get_argument()}"

    try:
      projects = subprocess.check_output(cmd, shell=True, text=True).splitlines()[:10]
    except subprocess.CalledProcessError:
      projects = []

    items = [
      ExtensionResultItem(
        icon='images/icon.png',
        name=project.split('/')[-1],
        description=project,
        on_enter=RunScriptAction(f"{ext.preferences["editor"]} {project}")
      ) for project in projects
    ]

    if not items:
      items.append(ExtensionResultItem(
        icon='images/icon.png',
        name='No projects found',
        description='No projects found in the specified folder',
        on_enter=HideWindowAction()
      ))

    return RenderResultListAction(items)

if __name__ == '__main__':
  Launcher().run()
