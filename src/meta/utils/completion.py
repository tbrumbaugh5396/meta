"""Shell completion utilities."""

import os
from pathlib import Path
from typing import List


BASH_COMPLETION = """# Meta-repo CLI bash completion

_meta_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="validate plan apply test exec lock deps conflicts rollback health config scaffold cache store gc status version"
    
    case "${prev}" in
        --component|-c|--env|-e|--manifests|-m)
            # Component completion
            if [ -d "components" ]; then
                COMPREPLY=($(compgen -W "$(ls components 2>/dev/null)" -- ${cur}))
            fi
            return 0
            ;;
        --env|-e)
            COMPREPLY=($(compgen -W "dev staging prod" -- ${cur}))
            return 0
            ;;
    esac
    
    if [[ ${cur} == -* ]]; then
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
    else
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
    fi
}

complete -F _meta_completion meta
"""

ZSH_COMPLETION = """# Meta-repo CLI zsh completion

_meta() {
    local -a commands
    commands=(
        'validate:Validate system'
        'plan:Show planned changes'
        'apply:Apply changes'
        'test:Run tests'
        'exec:Execute command'
        'lock:Manage lock files'
        'deps:Manage dependencies'
        'conflicts:Resolve conflicts'
        'rollback:Rollback components'
        'health:Check health'
        'config:Manage config'
        'scaffold:Scaffold components'
        'cache:Manage cache'
        'store:Manage store'
        'gc:Garbage collection'
        'status:Show status'
        'version:Show version'
    )
    
    _describe 'commands' commands
}

compdef _meta meta
"""

FISH_COMPLETION = """# Meta-repo CLI fish completion

complete -c meta -f -n '__fish_use_subcommand' -a 'validate' -d 'Validate system'
complete -c meta -f -n '__fish_use_subcommand' -a 'plan' -d 'Show planned changes'
complete -c meta -f -n '__fish_use_subcommand' -a 'apply' -d 'Apply changes'
complete -c meta -f -n '__fish_use_subcommand' -a 'test' -d 'Run tests'
complete -c meta -f -n '__fish_use_subcommand' -a 'exec' -d 'Execute command'
complete -c meta -f -n '__fish_use_subcommand' -a 'lock' -d 'Manage lock files'
complete -c meta -f -n '__fish_use_subcommand' -a 'deps' -d 'Manage dependencies'
complete -c meta -f -n '__fish_use_subcommand' -a 'conflicts' -d 'Resolve conflicts'
complete -c meta -f -n '__fish_use_subcommand' -a 'rollback' -d 'Rollback components'
complete -c meta -f -n '__fish_use_subcommand' -a 'health' -d 'Check health'
complete -c meta -f -n '__fish_use_subcommand' -a 'config' -d 'Manage config'
complete -c meta -f -n '__fish_use_subcommand' -a 'scaffold' -d 'Scaffold components'
complete -c meta -f -n '__fish_use_subcommand' -a 'cache' -d 'Manage cache'
complete -c meta -f -n '__fish_use_subcommand' -a 'store' -d 'Manage store'
complete -c meta -f -n '__fish_use_subcommand' -a 'gc' -d 'Garbage collection'
complete -c meta -f -n '__fish_use_subcommand' -a 'status' -d 'Show status'
complete -c meta -f -n '__fish_use_subcommand' -a 'version' -d 'Show version'
"""


def install_completion(shell: str) -> bool:
    """Install shell completion."""
    if shell == "bash":
        completion_file = Path.home() / ".bash_completion.d" / "meta"
        completion_file.parent.mkdir(parents=True, exist_ok=True)
        completion_file.write_text(BASH_COMPLETION)
        return True
    elif shell == "zsh":
        completion_file = Path.home() / ".zsh" / "completions" / "_meta"
        completion_file.parent.mkdir(parents=True, exist_ok=True)
        completion_file.write_text(ZSH_COMPLETION)
        return True
    elif shell == "fish":
        completion_file = Path.home() / ".config" / "fish" / "completions" / "meta.fish"
        completion_file.parent.mkdir(parents=True, exist_ok=True)
        completion_file.write_text(FISH_COMPLETION)
        return True
    else:
        return False


def get_completion_instructions(shell: str) -> str:
    """Get instructions for installing completion."""
    if shell == "bash":
        return """Add to ~/.bashrc:
source ~/.bash_completion.d/meta
"""
    elif shell == "zsh":
        return """Add to ~/.zshrc:
fpath=(~/.zsh/completions $fpath)
autoload -U compinit
compinit
"""
    elif shell == "fish":
        return """Completion installed automatically for fish.
Restart fish shell or run: source ~/.config/fish/completions/meta.fish
"""
    else:
        return f"Unsupported shell: {shell}"


