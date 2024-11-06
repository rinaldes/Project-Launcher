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
    editor = ext.preferences["editor"]
    folder = ext.preferences["folder"]
    cmd = f"find {folder} -type d -name .git -prune -exec dirname {{}} \; | rev | cut -d'/' -f1 | rev"

    if event.get_argument():
      cmd += f" | grep {event.get_argument()}"

    try:
      projects = subprocess.check_output(cmd, shell=True, text=True).splitlines()[:10]
    except subprocess.CalledProcessError:
      projects = []

    items = [
      ExtensionResultItem(
        icon='images/icon.png',
        name=project,
        description=f'{editor} {project}',
        on_enter=RunScriptAction(f"{editor} {folder}/{project}")
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
