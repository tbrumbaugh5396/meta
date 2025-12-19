"""Utility modules."""

# Explicitly import modules to make them available as a package
from meta.utils import logger
from meta.utils import manifest
from meta.utils import version
from meta.utils import git
from meta.utils import bazel
from meta.utils import lock
from meta.utils import dependencies
from meta.utils import packages
from meta.utils import environment_locks
from meta.utils import package_locks
from meta.utils import security
from meta.utils import licenses
from meta.utils import dependency_graph
from meta.utils import semver
from meta.utils import conflicts
from meta.utils import cache
from meta.utils import cache_keys
from meta.utils import content_hash
from meta.utils import store
from meta.utils import gc
from meta.utils import rollback
from meta.utils import remote_cache
from meta.utils import progress
# Phase 15-18 utilities (optional imports)
try:
    from meta.utils import templates_library
    from meta.utils import notifications
    from meta.utils import aliases
    from meta.utils import search
    from meta.utils import history
    from meta.utils import deployment
    from meta.utils import sync
    from meta.utils import review
    from meta.utils import monitoring_integration
    from meta.utils import optimization
    from meta.utils import compliance
    from meta.utils import versioning_strategies
except ImportError:
    pass
# Phase 20 utilities (optional imports)
try:
    from meta.utils import os_config
    from meta.utils import os_provisioning
    from meta.utils import os_state
    from meta.utils import os_build
    from meta.utils import os_deploy
    from meta.utils import os_monitoring
except ImportError:
    pass

__all__ = ['logger', 'manifest', 'version', 'git', 'bazel', 'lock', 'dependencies', 'packages', 
           'environment_locks', 'package_locks', 'security', 'licenses', 'dependency_graph',
           'semver', 'conflicts', 'cache', 'cache_keys', 'content_hash', 'store', 'gc',
           'rollback', 'remote_cache', 'progress', 'templates_library', 'notifications', 'aliases',
           'search', 'history', 'deployment', 'sync', 'review', 'monitoring_integration', 'optimization',
           'compliance', 'versioning_strategies', 'os_config', 'os_provisioning', 'os_state',
           'os_build', 'os_deploy', 'os_monitoring']
