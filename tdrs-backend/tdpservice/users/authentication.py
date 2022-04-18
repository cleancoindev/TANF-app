"""Define custom authentication class."""

from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication
import logging
logger = logging.getLogger(__name__)

class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    @staticmethod
    def authenticate(username=None, login_gov_uuid=None, hhs_id=None):
        """Authenticate user with the request and username."""
        User = get_user_model()
        logging.debug("CustomAuthentication::authenticate:hhs_id {}".format(hhs_id))
        logging.debug("CustomAuthentication::authenticate:login_gov_uuid {}".format(login_gov_uuid))
        logging.debug("CustomAuthentication::authenticate:username {}".format(username))
        try:
            if hhs_id:
                print("got to hhs block", flush=True)
                try:
                    user = User.objects.get(hhs_id=hhs_id)
                    logging.info("User.hhsid: {}".format(user.hhs_id))
                except User.DoesNotExist:  # 'user' likely None aka hhs_id hasn't been filled in, try to update it
                    print("Hit DNE error, did not find hhs_id. Will try to update.", flush=True)
                    User.objects.filter(username=username).update(hhs_id=hhs_id)
                    logging.debug("Updated user {} with hhs_id {}.".format(user.username, user.hhs_id))
                    # if 'username' doesn't exist in postgres then the below `return` triggers
                    # login.py::handler_user() to create new user w/ username and hhs_id
                except Exception as e:
                    print("hit general exception: {}".format(e), flush=True)
                    raise e
                finally:
                    hhs_user = User.objects.get(hhs_id=hhs_id)
                    print("hhs_user: {}".format(hhs_user), flush=True)
                    return hhs_user

            elif login_gov_uuid:
                return User.objects.get(login_gov_uuid=login_gov_uuid)
            else:
                return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
