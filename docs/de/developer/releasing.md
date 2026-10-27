[en](../../en-gb/developer/releasing.md) | de | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Veröffentlichen

Was vor einer Veröffentlichung zu tun ist, wie eine Veröffentlichung publiziert wird und wie die Home-Assistant-Version erhöht wird. Das Pushen eines Versions-Tags startet den Workflow `Release` in `.github/workflows/release.yml`, der das Tag prüft, die Prüfungen ausführt und ein GitHub-Release als Entwurf erstellt.

## Versionen

Eine Veröffentlichung ist ein GitHub-Release aus einem Versions-Tag auf `main`. Das Tag hat kein Präfix `v` und entspricht der Version in `custom_components/saj_local/manifest.json`, `pyproject.toml` und `frontend/package.json`. Ein stabiles Release ist `X.Y.Z` und eine Beta ist `X.Y.ZbN`, veröffentlicht als GitHub-Pre-Release. Die Betas vor dem ersten stabilen Release sind `1.0.0b1`, `1.0.0b2` und so weiter, das erste stabile Release ist `1.0.0`, und Semantic Versioning gilt ab `1.0.0`. Die Release-Notes stehen nur im GitHub-Release, und die Notes einer Beta nennen jede Änderung an einer Entität, einer gespeicherten Einstellung, einem Kartentyp oder einer Karteneinstellung seit der vorherigen Beta. Der Abschnitt [Veröffentlichungen](../../../.github/work/requirements.md#releases) der Projektanforderungen enthält die Regel.

## Vor einer Veröffentlichung

Führe diese Schritte auf `main` der Reihe nach aus.

1. **Führe `make ci` aus.** Die [Seite Prüfungen](checks.md) listet auf, was `make ci` ausführt.
2. **Führe `make docs-images` aus.** Die Benutzerdokumentation zeigt die Oberfläche, und CI erzeugt die Bilder nicht neu, daher braucht jede Veröffentlichung einen frischen Satz. Das Target braucht Docker. Führe das Target aus, sieh dir jedes geänderte Bild an, committe die geänderten Bilder in `docs/images/en-gb/` und führe `make docs-check` aus. Ein Lauf, der fehlschlägt, schreibt kein Bild, also veröffentliche nicht mit einem fehlgeschlagenen Lauf. Lies [Screenshots](documentation.md#screenshots), was der Lauf tut und warum jeder Messwert in einem Bild simuliert ist.
3. **Kopiere den Screenshot für die Website im selben Schritt.** Kopiere `docs/images/en-gb/cards-power-flow-card.png` nach `assets/images/saj-local-power-flow.png` im Repository `website` und committe die Kopie dort, weil die SAJ-Local-Seite auf `counterphase.dev` eine Kopie des Bildes zeigt. Keine Prüfung erkennt eine veraltete Kopie, weil CI in diesem Repository das Website-Repository nicht sehen kann.
4. **Führe `make release-check` aus.** Der Schritt erstellt ein Archiv aus `custom_components/saj_local/` und schlägt fehl, wenn dem Archiv `asset-manifest.json` oder das gebaute Karten-Bundle fehlt. Führe `make build` aus und committe zuerst das Bundle, wenn sich die Karten geändert haben.
5. **Setze die neue Version.** Setze die Version in `custom_components/saj_local/manifest.json`, `pyproject.toml` und `frontend/package.json`. Führe `uv lock` aus, damit `uv.lock` die Projektversion aufzeichnet, und führe `npm install --package-lock-only` in `frontend/` aus, damit `frontend/package-lock.json` die Version aufzeichnet. Führe `make release-check` aus, committe auf `main` und warte, bis CI besteht.

Die Screenshots sind der einzige Teil einer Veröffentlichung, den CI nicht prüfen kann. Eine Änderung, die ein Bild hinzufügt oder entfernt, lässt `make docs-check` durch die Regeln für unbenutzte und fehlende Bilder fehlschlagen. Eine Änderung an der Oberfläche, die ein Bild veralten lässt, lässt nichts fehlschlagen, daher hält Schritt 2 die Bilder aktuell.

## Eine Veröffentlichung publizieren

1. Pushe das Tag: `git tag 1.0.0b1`, dann `git push origin 1.0.0b1`.
2. Warte auf den Workflow `Release`. Der Workflow verlangt, dass der getaggte Commit auf `main` liegt, führt `make ci` über `ci.yml` aus und erstellt ein Entwurf-Release mit den von GitHub erzeugten Notes.
3. Öffne das Entwurf-Release und bearbeite die erzeugten Notes. Nenne bei einer Beta jede Änderung an einer Entität, einer gespeicherten Einstellung, einem Kartentyp oder einer Karteneinstellung seit der vorherigen Beta.
4. Drücke Publish.

Ein fehlgeschlagener Lauf erzeugt keinen Entwurf. Lösche das Tag mit `git push origin :refs/tags/<tag>` und `git tag -d <tag>`, repariere `main` und tagge erneut.

HACS bietet eine veröffentlichte Beta Benutzern an, die „Beta-Versionen anzeigen“ einschalten, und ein veröffentlichtes stabiles Release jedem Benutzer. Ein Benutzer ohne den Schalter bekommt die Spitze von `main`, bis `1.0.0` existiert, weshalb `main` vor jedem Push `make ci` bestehen muss.

## Die Home-Assistant-Version erhöhen

Die Home-Assistant-Version ist in mehreren Dateien festgelegt, die zusammen aktualisiert werden müssen, sonst laufen der Entwicklungscontainer, die Browser-Tests und der Screenshot-Lauf, CI, HACS und das Test-Harness auseinander:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, die Laufzeit des Entwicklungs-Home-Assistant.
2. `Dockerfile.playwright-home-assistant`: die Zeile `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` des Images, das `make test-browser-home-assistant` und `make docs-images` verwenden.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` für CI-Lint und mypy, **und** `pytest-homeassistant-custom-component==<passendes Release>`. Das Test-Harness bringt sein eigenes festgelegtes `homeassistant` mit, daher müssen die beiden Festlegungen aus demselben Home-Assistant-Release stammen, sonst lösen Lint und Tests verschiedene Kerne auf.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, der minimale Home-Assistant-Kern, den HACS durchsetzt.
5. `uv.lock`: führe `uv lock` nach der Änderung von `pyproject.toml` aus, damit die Lock-Datei die neuen Festlegungen aufzeichnet.

Prüfe die Paarung auf PyPI vor dem Committen: Das `requires_dist` von `pytest-homeassistant-custom-component` muss dasselbe `homeassistant==<X.Y.Z>` aufführen, das in `pyproject.toml` festgelegt ist.

Führe nach einer Erhöhung `make ci` und `make docs-images` aus, weil eine neue Home-Assistant-Version die Bildschirme ändern kann, die die Bilder zeigen.
