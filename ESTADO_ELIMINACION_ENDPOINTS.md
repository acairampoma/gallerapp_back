# Estado actual de eliminación (DELETE) – Sistema GalloApp

Este documento resume el comportamiento actual de los endpoints de eliminación y confirma que el borrado es "duro" (hard delete) y, en el caso de Pedigrí, incluye limpieza de relaciones y recursos.

## Resumen

- **Topes**: Hard delete del registro. Elimina video en Cloudinary si existe.
- **Peleas**: Hard delete del registro. Elimina video en Cloudinary si existe.
- **Vacunas**: Hard delete del registro mediante SQL. Sin recursos multimedia asociados.
- **Pedigrí (Gallo)**: Hard delete del gallo y limpieza asociada (fotos Cloudinary y registros relacionados como peleas, topes y vacunas). Si el gallo es principal en genealogía, elimina también la genealogía asociada (según implementación del endpoint actual).

---

## Endpoints y archivos

- **Topes**
  - Endpoint: `DELETE /topes/{tope_id}`
  - Archivo: `app/api/v1/topes.py` → función `delete_tope()`

- **Peleas**
  - Endpoint: `DELETE /peleas/{pelea_id}`
  - Archivo: `app/api/v1/peleas.py` → función `delete_pelea()`

- **Vacunas**
  - Endpoint: `DELETE /vacunas/{vacuna_id}`
  - Archivo: `app/api/v1/vacunas.py` → función `delete_vacuna()`

- **Pedigrí (Gallo)**
  - Endpoint usado por frontend: `DELETE /api/v1/gallos/{id}`
  - Backend: `app/api/v1/gallos_con_pedigri.py` → `@router.delete("/{gallo_id}")` función `delete_gallo()`

---

## Detalle del comportamiento por endpoint

### 1) Topes – `app/api/v1/topes.py`
- Valida propiedad: filtra por `Tope.user_id == current_user_id`.
- Si hay `video_url`, intenta eliminar el video en Cloudinary.
- Borrado: `db.delete(tope)` y `db.commit()` (hard delete).
- Respuesta: `{"message": "Tope con ID X eliminado exitosamente"}`.
- Errores: 404 si no existe o no pertenece; 500 en error de BD.

### 2) Peleas – `app/api/v1/peleas.py`
- Valida propiedad: filtra por `Pelea.user_id == current_user_id`.
- Si hay `video_url`, intenta eliminar el video en Cloudinary.
- Borrado: `db.delete(pelea)` y `db.commit()` (hard delete).
- Respuesta: `{"message": "Pelea con ID X eliminada exitosamente"}`.
- Errores: 404 si no existe o no pertenece; 500 en error de BD.

### 3) Vacunas – `app/api/v1/vacunas.py`
- Valida propiedad por JOIN con `gallos` (asegura que la vacuna sea de un gallo del usuario).
- Borrado: SQL directo `DELETE FROM vacunas WHERE id = :vacuna_id` y `commit` (hard delete).
- Respuesta: `{"success": true, "message": "Vacuna eliminada exitosamente"}`.
- Errores: 404 si no existe o no pertenece; 500 en error.

### 4) Pedigrí (Gallo) – `app/api/v1/gallos_con_pedigri.py`
- Ruta: `DELETE /api/v1/gallos/{gallo_id}`.
- Valida propiedad: `SELECT * FROM gallos WHERE id = :gallo_id AND user_id = :user_id`.
- Limpieza de recursos:
  - Elimina fotos del gallo en Cloudinary (por `foto_principal_url` / `url_foto_cloudinary` si existen).
  - Elimina registros relacionados del gallo: **peleas**, **topes** y **vacunas** (delete explícito vía SQL).
  - Si el gallo es "principal" del árbol (por `id_gallo_genealogico`), elimina la genealogía asociada.
- Borrado final: `DELETE FROM gallos WHERE id = :gallo_id AND user_id = :user_id` + `commit` (hard delete).
- Respuesta: `{"success": true, ...}` con mensaje de éxito.

---

## Flujo de eliminación – Pedigrí

1. Verifica existencia y ownership del gallo.
2. Elimina medios en Cloudinary asociados al gallo (si existen).
3. Elimina dependencias del gallo del usuario: peleas, topes y vacunas.
4. Si es gallo principal, elimina genealogía asociada (familia vinculada por `id_gallo_genealogico`).
5. Elimina el registro del gallo.
6. Commit de la transacción.

---

## Consideraciones

- Todos los endpoints implementan **hard delete** (no soft delete).
- Topes/Peleas incluyen limpieza de **Cloudinary** (videos). Pedigrí incluye limpieza de **fotos**.
- Vacunas no tienen medios asociados y eliminan con SQL.
- Las validaciones de propiedad están presentes en todos los casos (directa o vía JOIN).

---

## Ideas de mejora (futuras)

- Unificar formato de respuesta de DELETE (por ejemplo: `{ success, message, id }`).
- Envolver eliminación de Pedigrí en **transacción atómica** (context manager) para all-or-nothing.
- Validar reglas de negocio al borrar genealogía (confirmaciones explícitas si hay descendencia).
- Timeouts/reintentos para Cloudinary.
- Considerar **soft delete** si se requiere auditoría o recuperación.
