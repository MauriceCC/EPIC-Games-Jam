# Blockout de Whitechapel: cómo usar el script

> Dueño: División D. Archivos: [`build_blockout.py`](build_blockout.py), [`../../SourceData/D/blockout_layout.json`](../../SourceData/D/blockout_layout.json) y el diseño en [`../../SourceData/D/LEVEL_DESIGN.md`](../../SourceData/D/LEVEL_DESIGN.md).

## Flujo de trabajo

1. **Cambiar el nivel = editar el JSON**, no mover cubos a mano. Así cada cambio queda en Git y se puede revisar en un PR.
2. Validar y regenerar la vista previa **fuera de Unreal** (no hace falta abrir el editor):

   ```bash
   python Scripts/D/build_blockout.py --preview SourceData/D/blockout_preview.svg
   ```

   Abrir `SourceData/D/blockout_preview.svg` en el navegador. Si el script imprime `[ERROR]`, no generará nada en Unreal hasta que se corrija.
3. Generar el blockout **en Unreal**, cuando exista F0 (ver más abajo).

## Qué valida

- Zonas alineadas a la rejilla de 1 m y sin solapes.
- Cada conexión está sobre un borde compartido entre dos zonas.
- Con todas las puertas abiertas se llega a todas las zonas desde `Z_Start`. También muestra qué zonas son accesibles **sin** abrir puertas de C, para comprobar que no hay atajos en el Acto I.
- Coberturas dentro de una sola zona y a más de 0,5 m de los huecos de paso.
- Los puntos sugeridos para B y C (checkpoints, waypoints de Jack, evidencias…) caen en suelo libre y no chocan con la cobertura.

## Qué genera en Unreal

| Pieza | Regla |
|---|---|
| Suelo | Uno por zona, 20 cm de grosor, cara superior en Z = 0 |
| Muros exteriores | Anillo de 1 m alrededor del suelo. **3 m** en el lado de la cámara (sur/oeste) y **9 m** en el resto |
| Tabiques | 4 m de alto, 40 cm de grosor, entre zonas vecinas, salvo donde hay conexión |
| Verja cerrada | 3 m, material oscuro (`C_SquareRefuge`) |
| Huecos de puerta | Se dejan **abiertos**: C coloca ahí su `BP_Door` en `L_Whitechapel_Story` |
| Coberturas | Según la tabla `cover` del JSON |
| Etiquetas de zona | `TextRenderActor` **ocultos en juego** (solo orientan en el editor) |

Todas las piezas llevan la etiqueta `D_Blockout`, se agrupan en la carpeta `Blockout/` del Outliner y usan los materiales de rejilla de `LevelPrototyping` (si falta alguno, se usa el material básico del motor).

## Requisitos para ejecutarlo en Unreal

- [ ] **F0 terminado:** existen `L_Whitechapel` y su subnivel `L_Whitechapel_Geo`.
- [ ] **Plugin "Python Editor Script Plugin" activado.** Hoy **no** figura en `Unscripted.uproject`. Activarlo modifica el `.uproject`, que es responsabilidad del integrador: pedírselo a quien cierre F0 (ya está en la lista de `01_CONTRATOS §7`).
- [ ] Unreal cerrado durante `git pull`.

## Pasos en el editor

1. Abrir `L_Whitechapel`.
2. **Window → Levels** → doble clic en `L_Whitechapel_Geo` para hacerlo *current* (aparece resaltado). Si el nivel actual no es Geo, el script se detiene sin crear nada.
3. **Tools → Execute Python Script…** → elegir `Scripts/D/build_blockout.py`.
4. Revisar el **Output Log** (filtrar por `D_Blockout`). Debe terminar con `Listo: … piezas generadas`.
5. **Ctrl+Z** deshace toda la generación de una vez si algo sale mal.
6. Guardar **solo** `L_Whitechapel_Geo`. Si `_AI` o `_Story` aparecen con asterisco, no guardarlos.

Volver a ejecutar el script borra **solo** los actores con la etiqueta `D_Blockout` de Geo y los regenera. Si añades algo a mano en Geo, **no le pongas esa etiqueta** o se borrará en la siguiente ejecución.

## Después de generarlo (D-03 a D-05)

1. Con el persistente `L_Whitechapel` como *current* (y `git lfs lock` del `.umap`), colocar un **NavMeshBoundsVolume** con los valores que imprime el script, por ejemplo:
   `Location X=2700 Y=3000 Z=0` · `Brush Settings X=5600 Y=5800 Z=1000` (cm).
2. Pulsar **P** en el viewport: el verde debe cubrir las 11 zonas y cruzar todos los huecos.
3. Probar la cámara con el pawn de la plantilla (D-05) y anotar dónde se pierde de vista al jugador.
4. Repasar la lista de validación de `LEVEL_DESIGN.md §12`.

## Limitaciones conocidas

- El script **no se ha ejecutado todavía dentro de Unreal 5.8.4**: solo se ha probado la parte de validación y vista previa. La parte de editor usa la API estándar (`EditorActorSubsystem`, `LevelEditorSubsystem`), pero hay que confirmarla en la primera ejecución. Si falla alguna llamada, copiar el error del Output Log.
- Todo el suelo está a Z = 0: no hay rampas ni desniveles en v1.
- La altura de los muros depende de que la cámara quede al suroeste (yaw 45°). Si A cambia la cámara, ajustar la regla en el script (`low` / `high`).
