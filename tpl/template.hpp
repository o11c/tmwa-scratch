#ifndef {upper:{initials:{project_name}}_{module}_{identifier:{filename}}}
#define {upper:{initials:{project_name}}_{module}_{identifier:{filename}}}
//    {filename} - {description}
//
{prepend://
{reparse:{include:{conf_dir}/{license}}}}

#include "{root}.fwd"

namespace {lower:{initials:{project_name}}}
{{
namespace {module}
{{

}} // namespace {module}
}} // namespace {lower:{initials:{project_name}}}

#include "{root}.tcc"

#endif //{upper:{initials:{project_name}}_{module}_{identifier:{filename}}}
