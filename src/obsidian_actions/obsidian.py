"""
Interface with the Obsidian actions URI plugin (https://github.com/czottmann/obsidian-actions-uri?tab=readme-ov-file).

For this to work you will have to have the plugin installed in Obsidian
and have `xcall.app` installed.
"""

from collections import UserDict
from typing import Collection, Union

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
        self.commands = Commands(self)
        self.tags = Tags(self)
        self.notes = Notes(self)

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
        return {k.removeprefix("result-"): v for k, v in result.items()}

    def dataview_query(self, *sources, combine="and", fields=None):
        """
        Create a Dataview query.

        The `sources` can be one of:
        - tag: `vault.tags.<tag_name>`
        - folder
        - incoming links: `vault.notes["<note name>"].incoming`
        - outgoing links: `vault.notes["<note name>"].outgoing`
        Multiple source are combined using `combine` (can be set to "and" or "or").

        If `fields` is set a TABLE query is run.
        Otherwise, a LIST query is run.
        """
        if len(sources) == 0:
            raise ValueError("At least a single source should be provided for a dataview query.")
        if combine not in ("and", "or") and len(sources) > 1:
            raise ValueError(f"Sources can only be combined using and/or, not {combine}.")

        def source_to_string(source):
            if hasattr(source, "__self__") and source.__name__ == "incoming":
                return source.__self__.incoming_q
            if hasattr(source, "__self__") and source.__name__ == "outgoing":
                return source.__self__.outgoing_q
            return str(source)

        full_source = "FROM " + (" " + combine + " ").join([source_to_string(s) for s in sources])

        return DataviewQuery(self, full_source, fields=fields)

    def search(self, query, open=False) -> "Notes":
        """
        Run a search over all notes.

        If `open` the search will be opened within Obsidian.
        Otherwise, the results are returned as `notes`.
        """
        if open:
            return self("search", "open", query=query)
        else:
            result = self("search", "all-notes", query=query)
            return Notes(self, result)

    def daily_note(self, ):
        """Get today's daily note."""
        try:
            name = self("daily-note", "get-current", silent=True)["filepath"]
        except ChildProcessError as e:
            if "Note couldn't be found" not in e.args[0]:
                raise
            self.commands.daily_notes()
            name = self("daily-note", "get-current", silent=True)["filepath"]
        return Note(self, name)

    def weekly_note(self, ):
        """Get weekly note."""
        try:
            name = self("weekly-note", "get-current", silent=True)["filepath"]
        except ChildProcessError as e:
            if "Note couldn't be found" not in e.args[0]:
                raise
            self.commands.periodic_notes_open_weekly_note()
            name = self("weekly-note", "get-current", silent=True)["filepath"]
        return Note(self, name)

    def monthly_note(self, ):
        """Get monthly note."""
        try:
            name = self("monthly-note", "get-current", silent=True)["filepath"]
        except ChildProcessError as e:
            if "Note couldn't be found" not in e.args[0]:
                raise
            self.commands.periodic_notes_open_monthly_note()
            name = self("monthly-note", "get-current", silent=True)["filepath"]
        return Note(self, name)

    def quarterly_note(self, ):
        """Get quarterly note."""
        try:
            name = self("quarterly-note", "get-current", silent=True)["filepath"]
        except ChildProcessError as e:
            if "Note couldn't be found" not in e.args[0]:
                raise
            self.commands.periodic_notes_open_quarterly_note()
            name = self("quarterly-note", "get-current", silent=True)["filepath"]
        return Note(self, name)

    def yearly_note(self, ):
        """Get yearly note."""
        try:
            name = self("yearly-note", "get-current", silent=True)["filepath"]
        except ChildProcessError as e:
            if "Note couldn't be found" not in e.args[0]:
                raise
            self.commands.periodic_notes_open_yearly_note()
            name = self("yearly-note", "get-current", silent=True)["filepath"]
        return Note(self, name)

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

    @property
    def base_path(self, ) -> str:
        """Return base path of the vault."""
        if not hasattr(self, "_base_path"):
            self._base_path = self("info")["result-base-path"]
        return self._base_path

    @property
    def active_note(self, ) -> "Note":
        """Get the currently active note."""
        as_dict = self("note", "get-active")
        return Note(self, as_dict["filepath"])

    def note_create(self, filename, content=None, template=None, overwrite=False, silent=False) -> "Note":
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
        self(
            "note", "create",
            file=filename, apply=apply,
            content=content, template=template,
            if_exists="overwrite" if overwrite else "skip",
            silent=silent
        )
        return Note(self, filename)


class Tags:
    """All tags being used in the vault."""

    def __init__(self, vault: Vault, tags: Collection[Union[str, "Tag"]]=None):
        """Create new `Tags` for given `vault`."""
        self.vault = vault
        if tags is None:
            tags = self.vault("tags", "list")
        self.list = [tag if isinstance(tag, Tag) else Tag(tag) for tag in tags]

    @property
    def _attributes(self, ):
        """Return tags as dictionary."""
        return {tag.attribute_key: tag for tag in self.list}

    def __dir__(self, ):
        """Allow tags to ge accessed using autocomplete."""
        return ["list", "update"] + list(self._attributes.keys())

    def __getattr__(self, name: str):
        """Get a specific tag."""
        if name in self._attributes.keys():
            return self._attributes[name]
        raise AttributeError(f"Tag with name {name} is not used in this vault.")

    def __repr__(self, ):
        """Return result of `repr(tags)`."""
        return repr(self.list)

    def __str__(self, ):
        """Return result of `str(tags)`."""
        return str(self.list)


class Tag:
    """Represents a tag used in the vault."""

    def __init__(self, name: str):
        """Create a new tag with given `name`."""
        self.name = name.removeprefix("#")

    @property
    def attribute_key(self, ):
        """Key that can be used as attribute in python."""
        return self.name.replace("-", "_").replace("/", "__")

    def __repr__(self, ):
        """Return string representation of tag."""
        return "#" + self.name

class Notes(UserDict):
    """Collection of notes in the vault."""

    def __init__(self, vault: Vault, notes: Collection[Union[str, "Note"]]=None):
        """Create a new set of notes from the `vault`."""
        self.vault = vault
        if notes is None:
            notes = self.vault("note", "list")
        as_list = [note if isinstance(note, Note) else Note(vault, note) for note in notes]
        self.data = {note.name: note for note in as_list}

    def __repr__(self, ):
        """Return string representation of notes."""
        return repr(set(self.data.keys()))

    def __str__(self, ):
        """Return string representation of notes."""
        return str(set(self.data.keys()))


class Note:
    """Representation of a note within Obsidian."""

    def __init__(self, vault: Vault, name: str):
        """
        Create a new note.

        Attributes will be lazily loaded.
        """
        self.vault = vault
        self.name = name.removesuffix(".md")

    def _load_attributes(self, ):
        """Load the note and fill out any attributes."""
        if hasattr(self, "_content"):
            return
        reply_get = self.vault("note", "get", file=self.name)

        for param in [
            "filepath",
            "front-matter",
            "content",
            "properties",
            "body",
        ]:
            attr = "_" + param.replace("-", "_")
            setattr(self, attr, reply_get[param])

        self._fix_properties()

    def _fix_properties(self, ):
        """Fix issues with the default properties loading."""
        for key, value in self._properties.items():
            if isinstance(value, list) and all(isinstance(v, dict) for v in value):
                # list of dictionaries should just be a single dictionary
                self._properties[key] = {k: v for d in value for k, v in d.items()}

    @property
    def path_internal(self, ) -> str:
        """Return file path of note relative to vault root folder."""
        self._load_attributes()
        return self._filepath

    @property
    def path(self, ) -> str:
        """Return full path of note."""
        return self.vault.base_path + "/" + self.filepath

    @property
    def content(self, ) -> str:
        """Return entire content of note."""
        self._load_attributes()
        return self._content

    @property
    def body(self, ) -> str:
        """Return body of note excluding front matter."""
        self._load_attributes()
        return self._body

    @property
    def front_matter(self, ) -> str:
        """Return front matter of the note."""
        self._load_attributes()
        return self._front_matter

    @property
    def properties(self, ) -> dict:
        """Return properties of the note embedded in front matter."""
        self._load_attributes()
        return self._properties

    def incoming(self, ) -> Notes:
        """Return notes that link to this note."""
        return self.vault.dataview_query(self.incoming_q)()

    @property
    def incoming_q(self, ) -> str:
        """Return string representation of incoming links for dataview query."""
        return f"[[{self.name}]]"

    def outgoing(self, ) -> Notes:
        """Return notes linked from this node."""
        return self.vault.dataview_query(self.incoming_q)()

    @property
    def outgoing_q(self, ) -> str:
        """Return string representation of incoming links for dataview query."""
        return f"outgoing({self.incoming_q})"

    def append(self, content, below_headline=None, create_if_not_found=False, ensure_newline=False, silent=False):
        """
        Append `content` to this note.

        Appends `content` to the end of the note at `filename`.
        If `below_headline` is set, append below that headline instead.
        `below_headline` should contain the full exact line of how the headline appears in the note.
        """
        return self.vault(
            "note", "append",
            file=self.filepath, content=content,
            below_headline=below_headline,
            create_if_not_found=create_if_not_found,
            ensure_newline=ensure_newline,
            silent=silent
        )

    def prepend(self, content, below_headline=None, create_if_not_found=False, ensure_newline=False, silent=False):
        """
        Prepend `content` to this note.

        By default the `content` is placed just after the front matter.
        For more details see :meth:`note_append`.
        """
        return self.vault(
            "note", "prepend",
            file=self.filepath, content=content,
            below_headline=below_headline,
            create_if_not_found=create_if_not_found,
            ensure_newline=ensure_newline,
            silent=silent
        )

    def open(self, ):
        """Open this note in Obsidian."""
        return self.vault("note", "open", file=self.filepath)

    def replace(self, search: str, replace: str, silent=False, regex=False):
        """Replace text `search` with text `replace` within this note."""
        cmd = "search-regex-and-replace" if regex else "search-string-and-replace"
        return self.vault("note", cmd, file=self.filepath, search=search, replace=replace, silent=silent)

    def delete(self, trash=False):
        """
        Delete this note from Obsidian.

        Trash the note instead if `trash` is set to True.
        """
        return self.vault("note", "trash" if trash else "delete", file=self.filepath)

    def __repr__(self, ):
        """Represent note with its name."""
        return self.name + ".md"


class Commands(UserDict):
    """
    Dictionary of available Obsidian commands.

    Each command is available using its ID.
    Commands are also available as attributes.
    """

    def __init__(self, vault: Vault):
        """Create a new set of commands available in the `vault`."""
        self.vault = vault
        commands = self.vault("command", "list")
        as_list = [command if isinstance(command, Command) else Command(vault, **command) for command in commands]
        self.data = {command.id: command for command in as_list}

        self._attributes = {command.id.replace(":", "_").replace("-", "_"): command for command in as_list}

    def __dir__(self, ):
        """Allow tags to ge accessed using autocomplete."""
        return ["data", "update"] + list(self._attributes.keys())

    def __getattr__(self, name: str):
        """Get a specific tag."""
        if name in self._attributes.keys():
            return self._attributes[name]
        raise AttributeError(f"Command with id {name} is not used in this vault.")


class Command:
    """Command available in Obsidian."""

    def __init__(self, vault: Vault, id: str, name: str):
        """Create a new command representation with given `id` and `name`."""
        self.vault = vault
        self.id = id
        self.name = name

    def __call__(self, ):
        """Run a command in obsidian."""
        return self.vault("command", "execute", commands=self.id)

    def __repr__(self, ):
        """Return command name as string representation."""
        return self.name


class DataviewQuery:
    """Represents a Dataview query for the Obsidian vault."""

    def __init__(self, vault: Vault, from_statement: str, *statements: str, fields=None) -> None:
        """Create a dataview query of the vault consisting of the given statements."""
        self.vault = vault
        self.fields = fields
        self.from_statement = from_statement
        self.statements = statements

    @property
    def type(self, ):
        """Return the query type based on whether `fields` are set."""
        return "LIST" if self.fields is None else "TABLE"

    def __repr__(self, ):
        """Get string representation of the Dataview query."""
        if self.type == "TABLE":
            field_str = ", ".join(self.fields)
            first_line = f"TABLE {field_str}"
        else:
            first_line = self.type
        return "\n".join([first_line, self.from_statement] + list(self.statements))

    def __call__(self, ):
        """Run the query and return the result."""
        result = self.vault("dataview", self.type.lower() + "-query", dql=str(self))
        if self.type == "LIST":
            filenames = [link[2:].split("|")[0] for link in result]
            return Notes(self.vault, filenames)
        else:
            return result

    def where(self, clause: str):
        """Filter pages based on fields."""
        return DataviewQuery(self.vault, self.from_statement, *self.statements, "WHERE " + clause, fields=self.fields)

    def sort(self, field: str, ascending=False):
        """Sort results by a field."""
        cmd = field + " " + ("ASCENDING" if ascending else "DESCENDING")
        if len(self.statements) > 0 and self.statements[-1].startswith("SORT "):
            statements = self.statements[:-1] + (self.statements[-1] + ", " + cmd, )
        else:
            statements = self.statements + ("SORT " + cmd, )
        return DataviewQuery(self.vault, self.from_statement, *statements, fields=self.fields)

    def group_by(self, field: str, new_name=None):
        """Group results on a field."""
        if new_name is None:
            cmd = "GROUP BY " + field
        else:
            cmd = "GROUP BY " + field + " AS " + new_name
        return DataviewQuery(self.vault, self.from_statement, *self.statements, cmd, fields=self.fields)

    def flatten(self, field: str, new_name=None):
        """Flatten an array in every row yielding one resutl row per entry in the array."""
        if new_name is None:
            cmd = "FLATTEN " + field
        else:
            cmd = "FLATTEN " + field + " AS " + new_name
        return DataviewQuery(self.vault, self.from_statement, *self.statements, cmd, fields=self.fields)

    def limit(self, number: int):
        """Restrict the results to at most `number` values."""
        return DataviewQuery(self.vault, self.from_statement, *self.statements, "LIMIT " + str(number), fields=self.fields)
