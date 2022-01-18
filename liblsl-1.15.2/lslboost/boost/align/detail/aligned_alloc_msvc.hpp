/*
Copyright 2014 Glen Joseph Fernandes
(glenjofe@gmail.com)

Distributed under the Boost Software License, Version 1.0.
(http://www.boost.org/LICENSE_1_0.txt)
*/
#ifndef BOOST_ALIGN_DETAIL_ALIGNED_ALLOC_MSVC_HPP
#define BOOST_ALIGN_DETAIL_ALIGNED_ALLOC_MSVC_HPP

#include <boost/align/detail/is_alignment.hpp>
#include <boost/assert.hpp>
#include <malloc.h>

namespace lslboost {
namespace alignment {

inline void*
aligned_alloc(std::size_t alignment, std::size_t size) BOOST_NOEXCEPT
{
    BOOST_ASSERT(detail::is_alignment(alignment));
    return ::_aligned_malloc(size, alignment);
}

inline void
aligned_free(void* ptr) BOOST_NOEXCEPT
{
    ::_aligned_free(ptr);
}

} /* alignment */
} /* boost */

#endif
