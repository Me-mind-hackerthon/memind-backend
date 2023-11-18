from models import User
from auth import hash_password, create_access_token
from exceptions import SignInFailedError, UserAlreadyExist, UserNotFound, NicknameAlreadyExist
from schema import UserInfo, MessageOnlySchema

class SignIn:
    def __init__(self, session) -> None:
        self.session = session

    async def sign_in(self, user) -> Dict[str, str]:
        """ 로그인 """
        user_object = GetUserInfo().get_user_info(user.username)

        if(hash_password.HashPassword().verify_hash(user.password, user_object.password)):
            access_token = create_access_token(user_object.nickname)
            return {
                "access_token": access_token,
                "token_type": "Bearer"
            }
        raise SignInFailedError

class SignUp:
    def __init__(self, session) -> None:
        self.session = session

    async def sign_up(self, user: UserInfo) -> MessageOnlySchema:
        """ 회원가입 """
        user_exist = select(User).where(User.nickname == user.nickname)
        user_exist = self.session.exec(user_exist).first()

        if(user_exist):
            raise UserAlreadyExist

        hashed_password = hash_password.HashPassword().create_hash(user.password)

        user = User(
            nickname = user.nickname,
            password = hashed_password
        )

        self.session.add(user)
        self.session.commit()

        return {
            "message": "user created successfully"
        }

class GetUserInfo:
    def __init__(self, session):
        self.session = session

    async def get_user_info(self, user: UserInfo) -> Any:
        """ 해당 유저가 있는지를 확인하고 있다면 해당 유저의 정보를 리턴하는 함수 """
        try:
            user_exist = select(User).where(User.nickname == user.nickname)
            user_exist = self.session.exec(user_exist).one()
        except Exception as e:
            raise UserNotFound

        return user_exist

class DuplicateHandler:
    def __init__(self, session):
        self.session = session

    async def check_duplicate(self, nickname) -> MessageOnlySchema:
        """ 정보가 입력됐을 때, 해당 정보를 가진 유저가 있는제를 체크하는 함수 """
        try:
            user_exist = select(User).where(User.nickname == nickname)
            user_exist = self.session.exec(user_exist).one()
        except Exception as e:
            return {"message": "ok"}

        raise NicknameAlreadyExist