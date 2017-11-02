import environ

env = environ.Env()

GRADER_SOLUTION_MODEL = 'education.Solution'

GRADER_GRADE_PATH = "/grade"
GRADER_CHECK_PATH = "/check_result/{build_id}/"
GRADER_GET_NONCE_PATH = "/nonce"
GRADER_ADDRESS = env('GRADER_ADDRESS', default='https://grader.hackbulgaria.com')
GRADER_API_KEY = env('GRADER_API_KEY', default='')
GRADER_API_SECRET = env('GRADER_API_SECRET', default='')
GRADER_POLLING_COUNTDOWN = env.int('GRADER_POLLING_COUNTDOWN', default=2)
GRADER_RESUBMIT_COUNTDOWN = env.int('GRADER_RESUBMIT_COUNTDOWN', default=10)
