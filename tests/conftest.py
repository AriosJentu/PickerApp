import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from tests.test_config.fixtures.database import *
from tests.test_config.fixtures.client import *

from tests.test_config.fixtures.routes import *

from tests.test_config.fixtures.factories import *

from tests.test_config.fixtures.objects import *
from tests.test_config.fixtures.lists import *
