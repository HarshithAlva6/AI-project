import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..models.user import User as UserModel
from ..models.recipe import Recipe as RecipeModel
from ..models.food_item import FoodItem as FoodItemModel
from ..db import db

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

class RecipeType(SQLAlchemyObjectType):
    class Meta:
        model = RecipeModel

class FoodItemType(SQLAlchemyObjectType):
    class Meta:
        model = FoodItemModel

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_recipes = graphene.List(RecipeType)
    all_food_items = graphene.List(FoodItemType)

    def resolve_all_users(self, info):
        query = UserType.get_query(info)
        return query.all()

    def resolve_all_recipes(self, info):
        query = RecipeType.get_query(info)
        return query.all()

    def resolve_all_food_items(self, info):
        query = FoodItemType.get_query(info)
        return query.all()

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(lambda: UserType)

    def mutate(self, info, username, email, password):
        user = UserModel(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return CreateUser(user=user)

class CreateRecipe(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        ingredients = graphene.String()
        instructions = graphene.String()
        user_id = graphene.Int(required=True)  # Add user_id as a required argument

    recipe = graphene.Field(lambda: RecipeType)

    def mutate(self, info, title, description, ingredients, instructions, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            raise Exception("User not found")
        recipe = RecipeModel(title=title, description=description, ingredients=ingredients, instructions=instructions, user_id=user_id )
        db.session.add(recipe)
        db.session.commit()
        return CreateRecipe(recipe=recipe)

class CreateFoodItem(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        calories = graphene.Float()
        protein = graphene.Float()
        fat = graphene.Float()
        carbohydrates = graphene.Float()

    food_item = graphene.Field(lambda: FoodItemType)

    def mutate(self, info, name, calories=None, protein=None, fat=None, carbohydrates=None):
        food_item = FoodItemModel(name=name, calories=calories, protein=protein, fat=fat, carbohydrates=carbohydrates)
        db.session.add(food_item)
        db.session.commit()
        return CreateFoodItem(food_item=food_item)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_recipe = CreateRecipe.Field()
    create_food_item = CreateFoodItem.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
