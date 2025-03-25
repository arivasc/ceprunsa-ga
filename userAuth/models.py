from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserCeprunsaManager(BaseUserManager):
    def createUserWithGoogle(self, email):
        userCeprunsa = self.model(
            email=email,
        )
        userCeprunsa.save(using=self._db)
        return userCeprunsa
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        userCeprunsa = self.model(
            email=self.normalize_email(email),
            
        )

        userCeprunsa.set_password(password)
        userCeprunsa.save()
        return userCeprunsa

    def create_superuser(self, email, password=None):
        userCeprunsa = self.create_user(
            email=email,
            password=password
        )
        userCeprunsa.is_staff = True
        userCeprunsa.isSuperuser = True
        userCeprunsa.save()
        return userCeprunsa


class UserCeprunsa(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joinDate = models.DateTimeField(auto_now_add=True, db_column='join_date')
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')

    USERNAME_FIELD = 'email'

    objects = UserCeprunsaManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users_ceprunsa'
        
class RoleCeprunsa(models.Model):
    name = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=100)
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')
    
    class Meta:
        db_table = 'roles_ceprunsa'
    
class UserCeprunsaRoleRelation(models.Model):
    idUser = models.ForeignKey(UserCeprunsa, on_delete=models.CASCADE, db_column='id_user_ceprunsa')
    idRole = models.ForeignKey(RoleCeprunsa, on_delete=models.CASCADE, db_column='id_role_ceprunsa')
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')
    
    class Meta:
        db_table = 'user_ceprunsa_roles_relations'