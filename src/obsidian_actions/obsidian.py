"""
Interface with the Obsidian actions URI plugin (https://github.com/czottmann/obsidian-actions-uri?tab=readme-ov-file).

For this to work you will have to have the plugin installed in Obsidian
and have `xcall.app` installed.
"""

from .xcall import xcall


class Vault:
    """
    Represents an Obsidian vault.

    You will have to create a vault before running any actions.

    Actions are available as methods of the `Vault` class.
    """

    def __init__(self, name) -> None:
        """Prepare to run actions in Obsidian vault with the given `name`."""
        self.name = name

    def __call__(self, *actions, **kwargs):
        """
        Run one of the Action URIs.

        For a list of the available ones see https://zottmann.dev/obsidian-actions-uri/routes/.
        You do not have to include the vault name or "actions-uri" when calling this method.
        Some of the actions are available as direct method calls on this class.
        """
        use_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        result = xcall("obsidian", "actions-uri", *actions, vault=self.name, **use_kwargs)
        if len(result) == 1:
            return list(result.values())[0]
        return result

    def list_commands(self, ):
        """
        List available obsidian commands.

        These are the commands available in Obsidian from the Command Palette.
        In the return list each command is represented as a dictionary:
        - `{id: string, name: string}`
        """
        return self("command", "list")

    def execute_command(self, *commands: str, pause_in_secs=None):
        """
        Run the passed-in command or commands in sequence in the specified vault.

        - `commands`: command IDs (obtain from :func:`list_commmands`)
        - `pause_in_secs`: length of the pauls in seconds between commands.
        """
        command_string = ",".join(commands)
        return self("command", "execute", commands=command_string, pause_in_secs=pause_in_secs)

    def dataview_list_query(self, query: str):
        """
        Run a Dataview LIST query.

        Result is returned as a list.
        """
        return self("dataview", "list-query", dql=query)

    def dataview_table_query(self, query: str):
        """
        Run a Dataview TABLE query.

        Result is returned as a list of lists.
        """
        return self("dataview", "table-query", dql=query)

    def file_list(self, ):
        """List all files (not just notes) in the vault."""
        return self("file", "list")

    def file_get_active(self, ):
        """Return the currently active file."""
        return self("file", "get-active")

    def file_open(self, filename):
        """Open file in Obsidian."""
        return self("file", "open", file=filename)

    def file_rename(self, old_filename, new_filename, silent=False):
        """
        Rename `old_filename` to `new_filename`.

        By default the new file will be opened in Obsidian.
        Set `silent=True` to disable this.
        """
        return self("file", "rename", file=old_filename, new_filename=new_filename, silent=silent)

    def file_delete(self, filename):
        """Delete specific file."""
        return self("file", "delete", file=filename)

    def file_trash(self, filename):
        """Trash specific file."""
        return self("file", "trash", file=filename)

    def folder_list(self, ):
        """List folder paths."""
        return self("folder", "list")

    def folder_create(self, folder: str):
        """
        Create folder.

        Folder path needs to be relative to top-level vault directory.
        """
        return self("folder", "create", folder=folder)

    def folder_rename(self, old_folder: str, new_folder: str):
        """
        Rename folder path.

        Folder paths needs to be relative to top-level vault directory.
        """
        return self("folder", "create", folder=old_folder, new_foldername=new_folder)

    def folder_delete(self, folder: str):
        """
        Delete folder.

        Folder path needs to be relative to top-level vault directory.
        """
        return self("folder", "delete", folder=folder)

    def folder_trash(self, folder: str):
        """
        Trash folder.

        Folder path needs to be relative to top-level vault directory.
        """
        return self("folder", "trash", folder=folder)

    def info(self, ):
        """Return information about plugin and Obsidian."""
        return self("info")

    def note_list(self, ):
        """List all notes in the vault."""
        return self("note", "list")

    def note_get(self, name, silent=False, is_full_path=False):
        """
        Return a specific note by `name`.

        If `is_full_path` is set to True, `name` is assumed to be the full path.
        Otherwise, it is just the filename.
        The extension (`.md`) can be omitted.

        Result will be parsed in the note `body`, `content`, `filepath`, `front-matter`, `properties`.
        """
        getter = "get" if is_full_path else "get-first-named"
        return self("note", getter, file=name, silent=silent)

    def note_get_active(self, ):
        """
        Get the currently active note.

        Result will be parsed in the note `body`, `content`, `filepath`, `front-matter`, `properties`.
        """
        return self("note", "get-active")

    def note_open(self, name):
        """Open a specific note in Obsidian."""
        return self("note", "open", file=name)

    def note_create(self, filename, content=None, template=None, overwrite=False, silent=False):
        """
        Create a note at `filename` in Obsidian.

        By default an empty file is set.
        This can be updated by setting either `content` or `template`.
        Set `overwrite` is True to overwrite an existing file.
        Otherwise nothing is done if a file already exists.
        To append an existing note see :meth:`note_append`.

        Note content will be returned parsed into the note `body`, `content`, `filepath`, `front-matter`, `properties`.
        """
        if content is not None and template is not None:
            raise ValueError("Both `content` and `template` have been set when creating note. Please only set a signle one.")
        apply = "content" if template is None else "template"
        if template is None and content is None:
            content = ""
        return self(
            "note", "create",
            file=filename, apply=apply,
            content=content, template=template,
            if_exists="overwrite" if overwrite else "skip",
            silent=silent
        )

    def note_append(self, filename, content, below_headline=None, create_if_not_found=False, ensure_newline=False, silent=False):
        """
        Append `content` to a note.

        Appends `content` to the end of the note at `filename`.
        If `below_headline` is set, append below that headline instead.
        `below_headline` should contain the full exact line of how the headline appears in the note.
        """
        return self(
            "note", "append",
            file=filename, content=content,
            below_headline=below_headline,
            create_if_not_found=create_if_not_found,
            ensure_newline=ensure_newline,
            silent=silent
        )

    def note_preppend(self, filename, content, below_headline=None, create_if_not_found=False, ensure_newline=False, silent=False):
        """
        Prepend `content` to a note.

        By default the `content` is placed just after the front matter.
        For more details see :meth:`note_append`.
        """
        return self(
            "note", "prepend",
            file=filename, content=content,
            below_headline=below_headline,
            create_if_not_found=create_if_not_found,
            ensure_newline=ensure_newline,
            silent=silent
        )

    def tags_list(self, ):
        """List all tags used in the vault."""
        return self("tags", "list")
