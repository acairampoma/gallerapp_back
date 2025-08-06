import psycopg2
from app.core.config import settings
from urllib.parse import urlparse

def check_database_tables():
    """Verificar tablas existentes en la base de datos PostgreSQL"""
    
    # Parse DATABASE_URL
    result = urlparse(settings.DATABASE_URL)
    
    connection_params = {
        'database': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }
    
    print("🔍 Conectando a PostgreSQL Railway...")
    print(f"   Host: {connection_params['host']}")
    print(f"   Database: {connection_params['database']}")
    print(f"   Port: {connection_params['port']}")
    print("-" * 50)
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # 1. Verificar todas las tablas existentes
        print("\n📋 TABLAS EXISTENTES EN LA BASE DE DATOS:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        # 2. Buscar específicamente tablas relacionadas con vacunas
        print("\n💉 VERIFICANDO TABLAS DE VACUNAS:")
        vaccine_tables = [
            'vaccine_types',
            'vaccination_records', 
            'vaccination_schedules',
            'vaccination_alerts',
            'vacunas',
            'tipos_vacunas',
            'registros_vacunacion'
        ]
        
        for table_name in vaccine_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            if exists:
                print(f"   ✅ Tabla '{table_name}' EXISTE")
                
                # Mostrar columnas de la tabla
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = cursor.fetchall()
                for col in columns:
                    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                    print(f"      - {col[0]}: {col[1]} {nullable}")
            else:
                print(f"   ❌ Tabla '{table_name}' NO existe")
        
        # 3. Verificar si existen tablas de gallos/roosters
        print("\n🐓 VERIFICANDO TABLAS DE GALLOS:")
        rooster_tables = ['gallos', 'roosters', 'profiles', 'users']
        
        for table_name in rooster_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            if exists:
                print(f"   ✅ Tabla '{table_name}' EXISTE")
        
        cursor.close()
        conn.close()
        
        print("\n✨ Verificación completada")
        
    except Exception as e:
        print(f"\n❌ Error al conectar: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_database_tables()