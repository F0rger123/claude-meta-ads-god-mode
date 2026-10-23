"""Action classes. Every connector tool call is mapped to exactly one."""

READ = "read"
PREVIEW = "preview"                  # dry run / validate_only / preview call
CREATE = "create"                    # new campaign/ad set/ad/creative, PAUSED
CREATE_ACTIVE = "create_active"      # create with ACTIVE status: always blocked
UPDATE = "update"                    # names, copy, targeting tweaks, schedules
BUDGET = "budget"
BID = "bid"
ACTIVATE = "activate"                # anything that starts or resumes spend
PAUSE = "pause"
NEGATIVE_KEYWORDS = "negative_keywords"
CREATIVE_SWAP = "creative_swap"
GEO_EXPANSION = "geo_expansion"
AUDIENCE = "audience"
TRACKING = "tracking"                # pixel/dataset/conversion action changes
EXPERIMENT = "experiment"
CATALOG = "catalog"
DELETE = "delete"
BILLING = "billing"                  # payment methods, spend limits, invoices
ADMIN = "admin"                      # ownership, users, roles, tokens
UNKNOWN_WRITE = "unknown_write"

NON_MUTATING = {READ, PREVIEW}

# Never executed through Claude. The human does these in the platform UI.
ALWAYS_BLOCKED = {CREATE_ACTIVE, BILLING, ADMIN}

# Require a human yes in every automation mode, including full_auto.
ALWAYS_APPROVAL = {ACTIVATE, DELETE, TRACKING, GEO_EXPANSION, UNKNOWN_WRITE}

# Small changes guarded_auto may make when the client policy lists them.
GUARDABLE = {BUDGET, BID, PAUSE, NEGATIVE_KEYWORDS, CREATIVE_SWAP}

# Reduces or stops spend. Allowed (with approval) even in read_only/draft so an
# emergency stop is never locked out.
SPEND_REDUCING = {PAUSE}

ALL = NON_MUTATING | {CREATE, UPDATE, AUDIENCE, EXPERIMENT, CATALOG} | ALWAYS_BLOCKED | ALWAYS_APPROVAL | GUARDABLE
