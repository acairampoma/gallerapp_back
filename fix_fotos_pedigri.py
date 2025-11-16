"""
🔧 SCRIPT DE CORRECCIÓN: Problema de Fotos en Pedigrí

Este script implementa la solución al problema donde:
1. Gallos con fotos de Cloudinary no actualizan correctamente
2. Fotos adicionales sobrescriben la foto principal
3. Subir fotos en casillas 2 o 3 da error

Solución: Mejorar lógica del endpoint /fotos-multiples
"""

# Este es el código corregido para el endpoint

CODIGO_CORREGIDO = """
# 📸🔄 ACTUALIZAR FOTOS MÚLTIPLES DE GALLO (CORREGIDO)
@router.post("/{gallo_id}/fotos-multiples", response_model=dict)
async def actualizar_fotos_multiples_gallo(
    gallo_id: int,
    foto_1: Optional[UploadFile] = File(None, description="Foto 1 del gallo"),
    foto_2: Optional[UploadFile] = File(None, description="Foto 2 del gallo"),
    foto_3: Optional[UploadFile] = File(None, description="Foto 3 del gallo"),
    foto_4: Optional[UploadFile] = File(None, description="Foto 4 del gallo"),
    actualizar_principal: bool = Form(False, description="Forzar actualización de foto principal"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    '''
    📸 ACTUALIZAR HASTA 4 FOTOS DE UN GALLO EXISTENTE (MEJORADO)

    Permite subir hasta 4 fotos que se almacenan en el campo JSON fotos_adicionales:
    - Detecta si foto_principal_url es de Cloudinary (legacy)
    - Si es Cloudinary, permite actualización automática
    - Si es ImageKit, preserva la foto principal (a menos que actualizar_principal=True)
    - Primera foto subida se marca como principal si corresponde
    - Resto se marcan con orden secuencial
    '''
    try:
        # 1. Verificar que el gallo existe y pertenece al usuario
        gallo_query = text('''
            SELECT id, nombre, codigo_identificacion, fotos_adicionales, foto_principal_url
            FROM gallos
            WHERE id = :gallo_id AND user_id = :user_id
        ''')

        gallo_result = db.execute(gallo_query, {
            "gallo_id": gallo_id,
            "user_id": current_user_id
        }).first()

        if not gallo_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gallo con ID {gallo_id} no encontrado o no tienes permisos"
            )

        print(f"🔍 Gallo encontrado: {gallo_result.nombre} ({gallo_result.codigo_identificacion})")
        
        # 🔍 DETECTAR SI LA FOTO ACTUAL ES DE CLOUDINARY (LEGACY)
        foto_actual = gallo_result.foto_principal_url or ""
        es_cloudinary = 'cloudinary' in foto_actual.lower()
        
        if es_cloudinary:
            print(f"⚠️ FOTO LEGACY DETECTADA: {foto_actual[:50]}...")
            print(f"✅ Se permitirá actualización automática a ImageKit")

        # 2. Subir fotos a Storage y construir array JSON
        fotos_json = []
        fotos_subidas = 0
        foto_principal_url = None
        primera_foto_subida = None

        fotos = [foto_1, foto_2, foto_3, foto_4]

        for i, foto in enumerate(fotos):
            if foto and foto.filename and foto.size > 0:
                try:
                    print(f"📸 Subiendo foto {i+1}: {foto.filename}")

                    # Subir con multi_image_service (MODERNO - 2025)
                    folder = f"gallos/user_{current_user_id}/gallo_{gallo_id}"
                    file_name = f"gallo_{gallo_result.codigo_identificacion}_foto_{i+1}_{foto.filename}"
                    
                    upload_result = await multi_image_service.upload_single_image(
                        file=foto,
                        folder=folder,
                        file_name=file_name,
                        optimize=True
                    )

                    if upload_result:
                        # Guardar la primera foto subida
                        if primera_foto_subida is None:
                            primera_foto_subida = upload_result
                        
                        # Construir objeto de foto para JSON
                        foto_obj = {
                            "url": upload_result['url'],
                            "url_optimized": upload_result['url'],
                            "orden": i + 1,
                            "es_principal": False,  # Se marcará después según lógica
                            "descripcion": f"Foto {i+1}",
                            "file_id": upload_result.get('file_id'),
                            "uploaded_at": datetime.now().isoformat(),
                            "file_size": upload_result.get('size', foto.size),
                            "filename_original": foto.filename
                        }

                        fotos_json.append(foto_obj)
                        fotos_subidas += 1

                        print(f"✅ Foto {i+1} subida exitosamente: {upload_result['url']}")

                except Exception as foto_error:
                    print(f"❌ Error subiendo foto {i+1}: {foto_error}")
                    # Continuar con las demás fotos
                    continue

        if fotos_subidas == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo subir ninguna foto. Verifica que los archivos sean válidos."
            )

        # 3. LÓGICA MEJORADA: Decidir si actualizar foto_principal_url
        debe_actualizar_principal = (
            not gallo_result.foto_principal_url or  # No tiene foto principal
            es_cloudinary or  # Es foto de Cloudinary (legacy)
            actualizar_principal  # Usuario fuerza actualización
        )
        
        if debe_actualizar_principal and primera_foto_subida:
            # ACTUALIZAR FOTO PRINCIPAL + FOTOS ADICIONALES
            foto_principal_url = primera_foto_subida['url']
            
            # Marcar la primera foto como principal en el JSON
            if fotos_json:
                fotos_json[0]['es_principal'] = True
            
            update_fotos = text('''
                UPDATE gallos
                SET fotos_adicionales = :fotos_json,
                    foto_principal_url = :foto_principal,
                    url_foto_cloudinary = :foto_optimizada,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id AND user_id = :user_id
            ''')
            
            foto_optimizada = primera_foto_subida['url']
            
            db.execute(update_fotos, {
                "fotos_json": json.dumps(fotos_json),
                "foto_principal": foto_principal_url,
                "foto_optimizada": foto_optimizada,
                "id": gallo_id,
                "user_id": current_user_id
            })
            
            mensaje_accion = "Foto principal actualizada + fotos adicionales agregadas"
            if es_cloudinary:
                mensaje_accion += " (migrada de Cloudinary a ImageKit)"
            
            print(f"✅ {mensaje_accion}")
            
        else:
            # SOLO ACTUALIZAR FOTOS ADICIONALES (PRESERVAR FOTO PRINCIPAL)
            update_fotos = text('''
                UPDATE gallos
                SET fotos_adicionales = :fotos_json,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id AND user_id = :user_id
            ''')
            
            db.execute(update_fotos, {
                "fotos_json": json.dumps(fotos_json),
                "id": gallo_id,
                "user_id": current_user_id
            })
            
            foto_principal_url = gallo_result.foto_principal_url
            print(f"✅ Fotos adicionales actualizadas (foto principal preservada)")
        
        db.commit()

        print(f"✅ {fotos_subidas} fotos actualizadas en BD para gallo {gallo_result.nombre}")

        # 4. Retornar respuesta exitosa
        return {
            "success": True,
            "message": f"Se actualizaron {fotos_subidas} fotos exitosamente",
            "data": {
                "gallo_id": gallo_id,
                "gallo_nombre": gallo_result.nombre,
                "fotos_subidas": fotos_subidas,
                "foto_principal_url": foto_principal_url,
                "foto_principal_actualizada": debe_actualizar_principal,
                "era_cloudinary": es_cloudinary,
                "fotos_detalle": fotos_json,
                "total_fotos_almacenadas": len(fotos_json)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando fotos: {str(e)}"
        )
"""

print("📄 Código corregido generado en fix_fotos_pedigri.py")
print("📋 Revisar DIAGNOSTICO_PROBLEMA_FOTOS_PEDIGRI.md para más detalles")
