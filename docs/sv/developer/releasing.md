[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | sv

# Utgåvor

Vad du gör före en utgåva, hur en utgåva publiceras och hur Home Assistant-versionen höjs. Att pusha en versionstagg startar arbetsflödet `Release` i `.github/workflows/release.yml`, som kontrollerar taggen, kör kontrollerna och skapar ett utkast till en GitHub-utgåva.

## Versioner

En utgåva är en GitHub-utgåva som görs från en versionstagg på `main`. Taggen har inget prefix `v` och är lika med versionen i `custom_components/saj_local/manifest.json`, `pyproject.toml` och `frontend/package.json`. En stabil utgåva är `X.Y.Z` och en beta är `X.Y.ZbN`, publicerad som en förhandsutgåva på GitHub. Betorna före den första stabila utgåvan är `1.0.0b1`, `1.0.0b2` och så vidare, den första stabila utgåvan är `1.0.0`, och Semantic Versioning gäller från `1.0.0`. Versionsanteckningarna finns bara i GitHub-utgåvan, och anteckningarna för en beta namnger varje ändring av en entitet, en sparad inställning, en korttyp eller en kortinställning sedan den föregående betan. Avsnittet [Utgåvor](../../../.github/work/requirements.md#releases) i projektets krav håller regeln.

## Före en utgåva

Gör detta på `main`, i ordning.

1. **Kör `make ci`.** [Kontrollsidan](checks.md) listar vad `make ci` kör.
2. **Kör `make docs-images`.** Användardokumentationen visar gränssnittet, och CI genererar inte bilderna på nytt, så varje utgåva behöver en ny uppsättning. Målet kräver Docker. Kör målet, titta på varje ändrad bild, checka in de ändrade bilderna i `docs/images/en-gb/` och kör `make docs-check`. En körning som misslyckas skriver ingen bild, så ge inte ut med en misslyckad körning. Läs [Skärmbilder](documentation.md#skärmbilder) för vad körningen gör och varför varje avläsning i en bild är simulerad.
3. **Kopiera webbplatsens skärmbild i samma steg.** Kopiera `docs/images/en-gb/cards-power-flow-card.png` till `assets/images/saj-local-power-flow.png` i arkivet `website` och checka in kopian där, eftersom SAJ Local-sidan på `counterphase.dev` visar en kopia av bilden. Ingen kontroll fångar en föråldrad kopia, eftersom CI i det här arkivet inte kan se webbplatsens arkiv.
4. **Kör `make release-check`.** Steget gör ett arkiv av `custom_components/saj_local/` och misslyckas när arkivet saknar `asset-manifest.json` eller det byggda kortpaketet. Kör `make build` och checka in paketet först när korten har ändrats.
5. **Ange den nya versionen.** Ange versionen i `custom_components/saj_local/manifest.json`, `pyproject.toml` och `frontend/package.json`. Kör `uv lock` så att `uv.lock` registrerar projektversionen, och kör `npm install --package-lock-only` i `frontend/` så att `frontend/package-lock.json` registrerar versionen. Kör `make release-check`, checka in på `main` och vänta på att CI går igenom.

Skärmbilderna är den enda delen av en utgåva som CI inte kan kontrollera. En ändring som lägger till eller tar bort en bild får `make docs-check` att misslyckas genom reglerna för oanvänd och saknad bild. En ändring av gränssnittet som lämnar en bild föråldrad får inget att misslyckas, så steg 2 är det som håller bilderna aktuella.

## Publicera en utgåva

1. Pusha taggen: `git tag 1.0.0b1`, sedan `git push origin 1.0.0b1`.
2. Vänta på arbetsflödet `Release`. Arbetsflödet kräver att den taggade incheckningen finns på `main`, kör `make ci` genom `ci.yml` och skapar ett utkast till utgåva med GitHubs genererade anteckningar.
3. Öppna utkastet till utgåva och redigera de genererade anteckningarna. För en beta, namnge varje ändring av en entitet, en sparad inställning, en korttyp eller en kortinställning sedan den föregående betan.
4. Tryck på Publish.

En misslyckad körning gör inget utkast. Ta bort taggen med `git push origin :refs/tags/<tag>` och `git tag -d <tag>`, åtgärda `main` och tagga igen.

HACS erbjuder en publicerad beta till användare som slår på "Visa betaversioner" och en publicerad stabil utgåva till varje användare. En användare utan reglaget får toppen av `main` tills `1.0.0` finns, vilket är varför `main` måste klara `make ci` före varje push.

## Höja Home Assistant-versionen

Home Assistant-versionen är fastlåst i flera filer som måste uppdateras tillsammans, annars glider utvecklingscontainern, webbläsartesterna och skärmbildskörningen, CI, HACS och testramverket isär:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, körmiljön för utvecklings-Home Assistant.
2. `Dockerfile.playwright-home-assistant`: raden `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` i avbilden som `make test-browser-home-assistant` och `make docs-images` använder.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` för lint och mypy i CI, **och** `pytest-homeassistant-custom-component==<matching release>`. Testramverket levererar sin egen fastlåsta `homeassistant`, så de två låsningarna måste komma från samma Home Assistant-version, annars löser lint och tester olika kärnor.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, den lägsta Home Assistant-kärna som HACS kräver.
5. `uv.lock`: kör `uv lock` efter redigeringen av `pyproject.toml`, så att låsfilen registrerar de nya låsningarna.

Verifiera paret på PyPI innan du checkar in: `requires_dist` för `pytest-homeassistant-custom-component` måste lista samma `homeassistant==<X.Y.Z>` som är fastlåst i `pyproject.toml`.

Efter en höjning, kör `make ci` och `make docs-images`, eftersom en ny Home Assistant-version kan ändra de skärmar som bilderna visar.
