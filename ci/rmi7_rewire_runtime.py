from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one match in {path}, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def rewire_config() -> None:
    path = "reference/implementations/python/src/teo_reference/config.py"

    replace_once(
        path,
        'def _iter_model_candidates(value: Any, path: str = "routing"):\n',
        'def _iter_model_candidates(value: Any, path: str = "runtime_compatibility"):\n',
    )
    replace_once(
        path,
        '\n\n_EXECUTION_KEYS = ("primary", "executor", "executable_review")\n',
        '''\n\n_MODEL_IDENTITY_KEYS = {\n    "agent",\n    "model",\n    "profile",\n    "reasoning",\n    "reasoning_by_risk",\n    "preferred_implementations",\n    "fallbacks",\n}\n\n\ndef _iter_responsibility_model_identity(value: Any, path: str):\n    if isinstance(value, dict):\n        for key, nested in value.items():\n            current = f"{path}.{key}"\n            if key in _MODEL_IDENTITY_KEYS:\n                yield current\n            yield from _iter_responsibility_model_identity(nested, current)\n    elif isinstance(value, list):\n        for index, nested in enumerate(value):\n            yield from _iter_responsibility_model_identity(nested, f"{path}[{index}]")\n\n\n_EXECUTION_KEYS = ("primary", "executor", "executable_review")\n''',
    )
    replace_once(
        path,
        '    routing: dict[str, Any]\n    workers: dict[str, Any]\n',
        '    routing: dict[str, Any]\n    runtime_compatibility: dict[str, Any]\n    workers: dict[str, Any]\n',
    )
    replace_once(
        path,
        '            workers=_load_workers(\n',
        '            runtime_compatibility=_load_yaml(\n                root_path / "policy/routing/core/runtime-compatibility-defaults.yaml"\n            ),\n            workers=_load_workers(\n',
    )
    replace_once(
        path,
        '        workers = self.workers.get("workers")\n        specialists = self.specialists.get("specialists")\n',
        '''        workers = self.workers.get("workers")\n        runtime_worker_defaults = self.runtime_compatibility.get("worker_defaults")\n        runtime_task_routes = self.runtime_compatibility.get("task_routes")\n        runtime_task_routing_defaults = self.runtime_compatibility.get("task_routing_defaults")\n        runtime_fallback_order = self.runtime_compatibility.get("fallback_order")\n        runtime_specialist_profiles = self.runtime_compatibility.get("specialist_profiles")\n        specialists = self.specialists.get("specialists")\n''',
    )
    replace_once(
        path,
        '            "workers": workers,\n            "specialists": specialists,\n',
        '''            "workers": workers,\n            "runtime_worker_defaults": runtime_worker_defaults,\n            "runtime_task_routes": runtime_task_routes,\n            "runtime_task_routing_defaults": runtime_task_routing_defaults,\n            "runtime_fallback_order": runtime_fallback_order,\n            "runtime_specialist_profiles": runtime_specialist_profiles,\n            "specialists": specialists,\n''',
    )
    replace_once(
        path,
        '        assert isinstance(workers, dict)\n        assert isinstance(specialists, dict)\n',
        '''        assert isinstance(workers, dict)\n        assert isinstance(runtime_worker_defaults, dict)\n        assert isinstance(runtime_task_routes, dict)\n        assert isinstance(runtime_task_routing_defaults, dict)\n        assert isinstance(runtime_fallback_order, dict)\n        assert isinstance(runtime_specialist_profiles, dict)\n        assert isinstance(specialists, dict)\n''',
    )
    replace_once(
        path,
        '        known_models = _known_models(self.models)\n        reachable_pairs: set[tuple[str, str]] = set()\n',
        '''        known_models = _known_models(self.models)\n\n        for surface_name, surface in (("workers", self.workers), ("routing", self.routing)):\n            for identity_path in _iter_responsibility_model_identity(surface, surface_name):\n                issues.append(\n                    f"ERROR: model/provider implementation identity is not allowed in responsibility configuration: {identity_path}"\n                )\n\n        worker_names = set(workers)\n        compatibility_worker_names = set(runtime_worker_defaults)\n        if worker_names != compatibility_worker_names:\n            missing = sorted(worker_names - compatibility_worker_names)\n            extra = sorted(compatibility_worker_names - worker_names)\n            details: list[str] = []\n            if missing:\n                details.append("missing=" + ",".join(missing))\n            if extra:\n                details.append("extra=" + ",".join(extra))\n            issues.append(\n                "ERROR: runtime compatibility worker-default coverage must exactly match active workers: "\n                + "; ".join(details)\n            )\n\n        reachable_pairs: set[tuple[str, str]] = set()\n''',
    )
    old_worker_validation = '''            for source_key in ("preferred_implementations", "fallbacks"):\n                values = worker.get(source_key, [])\n                if not isinstance(values, list) or not values:\n                    issues.append(f"ERROR: worker {worker_name} requires a non-empty {source_key} list")\n                    continue\n                unknown_models = sorted(str(model) for model in values if str(model) not in known_models)\n                if unknown_models:\n                    issues.append(\n                        f"ERROR: worker {worker_name} references unregistered models in {source_key}: "\n                        + ", ".join(unknown_models)\n                    )\n'''
    new_worker_validation = '''            compatibility_defaults = runtime_worker_defaults.get(worker_name, {})\n            if not isinstance(compatibility_defaults, dict):\n                issues.append(f"ERROR: runtime compatibility defaults for worker {worker_name} must be a mapping")\n            else:\n                for source_key in ("preferred_implementations", "fallbacks"):\n                    values = compatibility_defaults.get(source_key, [])\n                    if not isinstance(values, list) or not values:\n                        issues.append(\n                            f"ERROR: runtime compatibility worker {worker_name} requires a non-empty {source_key} list"\n                        )\n                        continue\n                    unknown_models = sorted(str(model) for model in values if str(model) not in known_models)\n                    if unknown_models:\n                        issues.append(\n                            f"ERROR: runtime compatibility worker {worker_name} references unregistered models in {source_key}: "\n                            + ", ".join(unknown_models)\n                        )\n'''
    replace_once(path, old_worker_validation, new_worker_validation)
    replace_once(
        path,
        '        for path, candidate in _iter_model_candidates(self.routing):\n',
        '        for path, candidate in _iter_model_candidates(self.runtime_compatibility):\n',
    )
    replace_once(
        path,
        '        for route_name, route in routing.items():\n            if not isinstance(route, dict):\n                issues.append(f"ERROR: implementation route {route_name} must be a mapping")\n',
        '        for route_name, route in runtime_task_routes.items():\n            if not isinstance(route, dict):\n                issues.append(f"ERROR: runtime compatibility task route {route_name} must be a mapping")\n',
    )
    replace_once(
        path,
        '                    f"ERROR: route {route_name} has no explicit model- and provider-diverse verifier candidate"\n',
        '                    f"ERROR: runtime compatibility route {route_name} has no explicit model- and provider-diverse verifier candidate"\n',
    )
    replace_once(
        path,
        '    def worker_registry(self) -> dict[str, Any]:\n        return self.workers["workers"]\n\n',
        '''    def worker_registry(self) -> dict[str, Any]:\n        return self.workers["workers"]\n\n    @property\n    def runtime_compatibility_defaults(self) -> dict[str, Any]:\n        return self.runtime_compatibility\n\n    @property\n    def worker_runtime_defaults(self) -> dict[str, Any]:\n        return self.runtime_compatibility["worker_defaults"]\n\n    @property\n    def runtime_task_routes(self) -> dict[str, Any]:\n        return self.runtime_compatibility["task_routes"]\n\n    @property\n    def runtime_task_routing_defaults(self) -> dict[str, Any]:\n        return self.runtime_compatibility["task_routing_defaults"]\n\n    @property\n    def runtime_fallback_order(self) -> dict[str, Any]:\n        return self.runtime_compatibility["fallback_order"]\n\n    @property\n    def runtime_specialist_profiles(self) -> dict[str, Any]:\n        return self.runtime_compatibility["specialist_profiles"]\n\n''',
    )


def rewire_engine() -> None:
    path = "reference/implementations/python/src/teo_reference/engine.py"
    replace_once(
        path,
        '''        worker_entry = self.config.worker_registry[worker]\n        allowed = set(str(item) for item in worker_entry.get("preferred_implementations", []))\n        allowed.update(str(item) for item in worker_entry.get("fallbacks", []))\n''',
        '''        worker_defaults = self.config.worker_runtime_defaults[worker]\n        allowed = set(str(item) for item in worker_defaults.get("preferred_implementations", []))\n        allowed.update(str(item) for item in worker_defaults.get("fallbacks", []))\n''',
    )
    replace_once(
        path,
        '        route = self.config.implementation_routes.get(task_type, {})\n',
        '        route = self.config.runtime_task_routes.get(task_type, {})\n',
    )
    replace_once(
        path,
        '            choice = self._choice(candidate, f"routing.{task_type}.{key}")\n',
        '            choice = self._choice(candidate, f"runtime_compatibility.task_routes.{task_type}.{key}")\n',
    )
    # _base_selection_preferences has a second route lookup.
    replace_once(
        path,
        '        route = self.config.implementation_routes.get(task_type, {})\n        preferences: list[dict[str, Any]] = []\n',
        '        route = self.config.runtime_task_routes.get(task_type, {})\n        preferences: list[dict[str, Any]] = []\n',
    )
    replace_once(
        path,
        '                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)\n',
        '                add(route.get(key), f"runtime_compatibility.task_routes.{task_type}.{key}", defer_if_worker_disallowed=True)\n',
    )
    replace_once(
        path,
        '                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)\n            worker_entry = self.config.worker_registry[worker]\n            for source_key in ("preferred_implementations", "fallbacks"):\n                for model in worker_entry.get(source_key, []):\n                    add({"agent": "registry", "model": model}, f"workers.{worker}.{source_key}")\n',
        '                add(route.get(key), f"runtime_compatibility.task_routes.{task_type}.{key}", defer_if_worker_disallowed=True)\n            worker_defaults = self.config.worker_runtime_defaults[worker]\n            for source_key in ("preferred_implementations", "fallbacks"):\n                for model in worker_defaults.get(source_key, []):\n                    add({"agent": "registry", "model": model}, f"runtime_compatibility.worker_defaults.{worker}.{source_key}")\n',
    )
    replace_once(
        path,
        '                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)\n            for model in self.config.worker_registry[worker].get("fallbacks", []):\n                add({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")\n            family = self._fallback_family(capabilities)\n            for candidate in self.config.routing.get("fallback_order", {}).get(family, []):\n                add(candidate, f"fallback_order.{family}", defer_if_worker_disallowed=True)\n',
        '                add(route.get(key), f"runtime_compatibility.task_routes.{task_type}.{key}", defer_if_worker_disallowed=True)\n            for model in self.config.worker_runtime_defaults[worker].get("fallbacks", []):\n                add({"agent": "registry", "model": model}, f"runtime_compatibility.worker_defaults.{worker}.fallbacks")\n            family = self._fallback_family(capabilities)\n            for candidate in self.config.runtime_fallback_order.get(family, []):\n                add(candidate, f"runtime_compatibility.fallback_order.{family}", defer_if_worker_disallowed=True)\n',
    )
    replace_once(
        path,
        '                add(route.get(key), f"routing.{task_type}.{key}")\n',
        '                add(route.get(key), f"runtime_compatibility.task_routes.{task_type}.{key}")\n',
    )
    replace_once(
        path,
        '                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)\n            for model in self.config.worker_registry[worker].get("fallbacks", []):\n                add({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")\n            for candidate in self.config.routing.get("fallback_order", {}).get("general_reasoning", []):\n                add(candidate, "fallback_order.general_reasoning", defer_if_worker_disallowed=True)\n',
        '                add(route.get(key), f"runtime_compatibility.task_routes.{task_type}.{key}", defer_if_worker_disallowed=True)\n            for model in self.config.worker_runtime_defaults[worker].get("fallbacks", []):\n                add({"agent": "registry", "model": model}, f"runtime_compatibility.worker_defaults.{worker}.fallbacks")\n            for candidate in self.config.runtime_fallback_order.get("general_reasoning", []):\n                add(candidate, "runtime_compatibility.fallback_order.general_reasoning", defer_if_worker_disallowed=True)\n',
    )
    replace_once(
        path,
        '                f"No transitional runtime authority/preferences are defined for {task_type}/{worker}/{role}"\n',
        '                f"No runtime compatibility preferences are defined for {task_type}/{worker}/{role}"\n',
    )


def rewire_specialists() -> None:
    path = "reference/implementations/python/src/teo_reference/specialist_routing.py"
    replace_once(
        path,
        'SPECIALIST_MODEL_POLICY = "policy/routing/core/specialist-model-routing.yaml"\n',
        'SPECIALIST_SELECTION_POLICY = "policy/routing/core/specialist-selection-policy.yaml"\n',
    )
    replace_once(
        path,
        '''    Specialist policy may elevate effective risk and supply ordered implementation/\n    reasoning preferences. Actual primary, fallback, and verifier choices remain owned\n    by the runtime selection lifecycle; this layer no longer overwrites a completed\n    DispatchRecord with static model choices.\n''',
        '''    Specialist responsibility remains model- and provider-neutral. The specialist policy\n    may elevate effective risk and assign a provider-neutral selection profile. Concrete\n    compatibility defaults for that profile are resolved separately and still pass through\n    the runtime selection lifecycle.\n''',
    )
    replace_once(
        path,
        '        self._specialist_model_policy = self._load_specialist_model_policy()\n        self._validate_specialist_model_policy()\n',
        '        self._specialist_selection_policy = self._load_specialist_selection_policy()\n        self._validate_specialist_selection_policy()\n',
    )
    start = '''    def _load_specialist_model_policy(self) -> dict[str, Any]:\n        path = Path(self.config.root) / SPECIALIST_MODEL_POLICY\n        if not path.is_file():\n            raise SpecialistRoutingError(f"Specialist model-routing policy not found: {path}")\n        data = yaml.safe_load(path.read_text(encoding="utf-8"))\n        if not isinstance(data, dict):\n            raise SpecialistRoutingError("Specialist model-routing policy root must be a mapping")\n        if data.get("status") != "active":\n            raise SpecialistRoutingError("Specialist model-routing policy must be active")\n        if not isinstance(data.get("templates"), dict) or not isinstance(data.get("specialists"), dict):\n            raise SpecialistRoutingError("Specialist model-routing policy requires templates and specialists")\n        return data\n'''
    replacement = '''    def _load_specialist_selection_policy(self) -> dict[str, Any]:\n        path = Path(self.config.root) / SPECIALIST_SELECTION_POLICY\n        if not path.is_file():\n            raise SpecialistRoutingError(f"Specialist selection policy not found: {path}")\n        data = yaml.safe_load(path.read_text(encoding="utf-8"))\n        if not isinstance(data, dict):\n            raise SpecialistRoutingError("Specialist selection policy root must be a mapping")\n        if data.get("status") != "active":\n            raise SpecialistRoutingError("Specialist selection policy must be active")\n        if not isinstance(data.get("profiles"), dict) or not isinstance(data.get("specialists"), dict):\n            raise SpecialistRoutingError("Specialist selection policy requires profiles and specialists")\n        return data\n'''
    replace_once(path, start, replacement)
    start_validate = path
    # Replace the complete validator/template lookup block by slicing between method markers.
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    begin = text.index('    def _provider_for_model(self, model: str) -> str | None:\n')
    end = text.index('    @staticmethod\n    def _specialist_preference(', begin)
    block = '''    def _provider_for_model(self, model: str) -> str | None:\n        entry = self._model_entry(model)\n        provider = entry.get("provider_family")\n        return str(provider) if provider else None\n\n    def _validate_specialist_selection_policy(self) -> None:\n        profiles = self._specialist_selection_policy["profiles"]\n        assignments = self._specialist_selection_policy["specialists"]\n        compatibility_profiles = self.config.runtime_specialist_profiles\n        registered = set(self.config.specialist_registry)\n        assigned = set(assignments)\n        if registered != assigned:\n            missing = sorted(registered - assigned)\n            extra = sorted(assigned - registered)\n            details = []\n            if missing:\n                details.append("missing=" + ",".join(missing))\n            if extra:\n                details.append("extra=" + ",".join(extra))\n            raise SpecialistRoutingError(\n                "Specialist selection-profile coverage must exactly match the active registry: "\n                + "; ".join(details)\n            )\n\n        if set(profiles) != set(compatibility_profiles):\n            raise SpecialistRoutingError(\n                "Model-neutral specialist profiles and runtime compatibility profiles must match exactly"\n            )\n\n        for specialist, assignment in assignments.items():\n            if not isinstance(assignment, dict) or not assignment.get("selection_profile"):\n                raise SpecialistRoutingError(f"Specialist {specialist} has no selection profile")\n            profile_name = str(assignment["selection_profile"])\n            if profile_name not in profiles:\n                raise SpecialistRoutingError(\n                    f"Specialist {specialist} references unknown selection profile {profile_name}"\n                )\n            compatibility = compatibility_profiles.get(profile_name)\n            if not isinstance(compatibility, dict):\n                raise SpecialistRoutingError(\n                    f"Selection profile {profile_name} has no runtime compatibility defaults"\n                )\n            providers: list[str] = []\n            models: list[str] = []\n            for key in ("primary", "fallback", "verifier"):\n                candidate = compatibility.get(key)\n                if not isinstance(candidate, dict) or not candidate.get("model"):\n                    raise SpecialistRoutingError(\n                        f"Runtime compatibility profile {profile_name} is missing {key}"\n                    )\n                model = str(candidate["model"])\n                provider = self._provider_for_model(model)\n                if not provider:\n                    raise SpecialistRoutingError(\n                        f"Runtime compatibility profile {profile_name} references model without provider metadata: {model}"\n                    )\n                models.append(model)\n                providers.append(provider)\n            if len(set(models)) != 3:\n                raise SpecialistRoutingError(\n                    f"Runtime compatibility profile {profile_name} must use distinct primary, fallback and verifier models"\n                )\n            if len(set(providers)) != 3:\n                raise SpecialistRoutingError(\n                    f"Runtime compatibility profile {profile_name} must preserve three-provider primary/fallback/verifier diversity"\n                )\n\n    def _selection_profile_for(self, specialist: str) -> tuple[str, dict[str, Any]]:\n        assignment = self._specialist_selection_policy["specialists"][specialist]\n        profile_name = str(assignment["selection_profile"])\n        return profile_name, self.config.runtime_specialist_profiles[profile_name]\n\n'''
    target.write_text(text[:begin] + block + text[end:], encoding="utf-8")

    replace_once(
        path,
        '        worker_entry = self.config.worker_registry[worker]\n',
        '        worker_defaults = self.config.worker_runtime_defaults[worker]\n',
    )
    replace_once(
        path,
        '            for model in worker_entry.get("preferred_implementations", [])\n',
        '            for model in worker_defaults.get("preferred_implementations", [])\n',
    )
    replace_once(
        path,
        '                "source": f"workers.{worker}.preferred_implementations.documentation_recovery",\n',
        '                "source": f"runtime_compatibility.worker_defaults.{worker}.preferred_implementations.documentation_recovery",\n',
    )
    replace_once(
        path,
        '        template_name, template = self._template_for(specialist)\n        source = f"{SPECIALIST_MODEL_POLICY}.templates.{template_name}"\n',
        '        profile_name, template = self._selection_profile_for(specialist)\n        source = f"policy/routing/core/runtime-compatibility-defaults.yaml.specialist_profiles.{profile_name}"\n',
    )


def main() -> None:
    rewire_config()
    rewire_engine()
    rewire_specialists()


if __name__ == "__main__":
    main()
