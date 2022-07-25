from django.db import models

from django.contrib.auth.models import User

from django.db.models import Sum

class Category(models.Model): #Создание таблицы Категории
    name=models.CharField(max_length=255, unique=True)

class PostCategory(models.Model): #Промежуточная таблица для связи сообщения и категории 1-∞
    id_post=models.ForeignKey("Post", on_delete = models.CASCADE)
    id_category = models.ForeignKey('Category', on_delete = models.CASCADE)

class Comments(models.Model): #Комментарии к новости
    id_post=models.ForeignKey('Post', on_delete=models.CASCADE) # Ключ к новости
    text=models.TextField() # Текст комментария
    date=models.DateTimeField(auto_now_add = True) # Когда добавлен
    sum_rank=models.IntegerField(default=0) #Рейтинг коммента
    id_users=models.ForeignKey(User, on_delete=models.CASCADE) # Ключ связи для Юзверя

    def like(self):  # Повышение рейтинга
        self.sum_rank=self.sum_rank+1
        self.save()

    def dislike(self):   # Понижение рейтинга
        if self.sum_rank>0:
            self.sum_rank=self.sum_rank-1
            self.save()

POSITIONS = [('news', 'Новости'), ('article', 'Статьи')] # Заголовок новость/статья

class Post(models.Model): #Таблица сообщения
    head_article=models.CharField(max_length=255) #Название сообщения
    text_post=models.TextField() #Текст сообщения
    date=models.DateTimeField(auto_now_add = True) # Время когда добавлено
    type_post=models.CharField(max_length = 20, choices = POSITIONS, default = 'news') #Тип. Сообщения статья или новость из кортежа
    sum_rank = models.IntegerField ( default=0 ) # Рейтинг изначально на ноль
    id_author=models.ForeignKey('Author', on_delete=models.CASCADE) # Тип связи с автором
    category=models.ManyToManyField('Category', through=PostCategory) # Тип связи с категорией сообщения


    def like(self): # Лайк
        self.sum_rank = self.sum_rank+1
        self.save()

    def dislike(self):
        if self.sum_rank > 0: #Дизлайк
            self.sum_rank = self.sum_rank-1
            self.save ()

    def preview(self):
        return self.text_post[0:124]

class Author(models.Model): # Таблица автора
    full_name=models.CharField(max_length=255) # Имя автора
    e_mail=models.EmailField(max_length=150, null=True) # Мыло
    rank=models.IntegerField(default=0) # Рейтинг блогера
    id_users=models.OneToOneField(User, on_delete=models.DO_NOTHING) # Тип связи с Юзверем

    def update_rating (self): # Обновление рейтинга
        a=Post.objects.filter(id_author=self.id).aggregate(Sum('sum_rank'))['sum_rank__sum']*3 # На сообщение
        b=Comments.objects.filter(id_users=self.id_users).aggregate(Sum('sum_rank'))['sum_rank__sum'] # На коммент
        c = Post.objects.filter(id_author=self.id).values('id') #Список связанных сообщений
        d=0 # счетчик
        for i in c:
            com=Comments.objects.filter ( id_post=i['id'] ).aggregate( Sum ( 'sum_rank' ) )['sum_rank__sum']
            if com!=None: #Проверка счетчика на ноль
                d+=com
        self.rank=a+b+d
        self.save()

