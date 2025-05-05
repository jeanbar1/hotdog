import boto3
from django.conf import settings

def test_s3_connection():
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("✅ Conexão com S3 bem-sucedida!")
        print(f"Arquivos no bucket: {len(response.get('Contents', []))}")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cardapio.settings")
    from django.conf import settings
    test_s3_connection()