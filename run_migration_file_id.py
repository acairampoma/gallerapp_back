"""
🔧 Script de migración para agregar columnas file_id
Ejecuta la migración SQL de forma segura
"""
import sys
from sqlalchemy import text
from app.database import engine

def run_migration():
    """Ejecutar migración para agregar columnas file_id"""
    
    print("=" * 60)
    print("🔧 MIGRACIÓN: Agregar columnas file_id")
    print("=" * 60)
    
    migrations = [
        {
            "name": "peleas.file_id",
            "sql": "ALTER TABLE peleas ADD COLUMN IF NOT EXISTS file_id VARCHAR(255)"
        },
        {
            "name": "topes.file_id",
            "sql": "ALTER TABLE topes ADD COLUMN IF NOT EXISTS file_id VARCHAR(255)"
        },
        {
            "name": "peleas_evento.file_id",
            "sql": "ALTER TABLE peleas_evento ADD COLUMN IF NOT EXISTS file_id VARCHAR(255)"
        },
        {
            "name": "pagos_pendientes.comprobante_file_id",
            "sql": "ALTER TABLE pagos_pendientes ADD COLUMN IF NOT EXISTS comprobante_file_id VARCHAR(255)"
        }
    ]
    
    with engine.connect() as conn:
        # Iniciar transacción
        trans = conn.begin()
        
        try:
            for migration in migrations:
                print(f"\n📝 Ejecutando: {migration['name']}")
                print(f"   SQL: {migration['sql']}")
                
                conn.execute(text(migration['sql']))
                print(f"   ✅ Completado")
            
            # Commit de todas las migraciones
            trans.commit()
            print("\n" + "=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            
            # Verificar columnas
            print("\n🔍 Verificando columnas agregadas...")
            verify_sql = text("""
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name IN ('peleas', 'topes', 'peleas_evento', 'pagos_pendientes')
                  AND column_name IN ('file_id', 'comprobante_file_id')
                ORDER BY table_name, column_name
            """)
            
            result = conn.execute(verify_sql)
            rows = result.fetchall()
            
            if rows:
                print("\n📊 Columnas agregadas:")
                for row in rows:
                    print(f"   ✅ {row[0]}.{row[1]} ({row[2]}, nullable={row[3]})")
            else:
                print("   ⚠️ No se encontraron las columnas (puede ser normal en algunas BD)")
            
            return True
            
        except Exception as e:
            # Rollback en caso de error
            trans.rollback()
            print("\n" + "=" * 60)
            print(f"❌ ERROR EN MIGRACIÓN: {e}")
            print("=" * 60)
            print("🔄 Rollback ejecutado - Base de datos sin cambios")
            return False

if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE: Esta migración agregará columnas a la base de datos")
    print("   Asegúrate de tener un backup antes de continuar\n")
    
    respuesta = input("¿Deseas continuar? (si/no): ").strip().lower()
    
    if respuesta in ['si', 's', 'yes', 'y']:
        success = run_migration()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Migración cancelada por el usuario")
        sys.exit(1)
