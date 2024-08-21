graph_query = """
        query getVisitorReviews($input: VisitorReviewsInput) {
            visitorReviews(input: $input) {
                items {
                    id
                    rating
                    author {
                        id
                        nickname
                        from
                        imageUrl
                        borderImageUrl
                        objectId
                        url
                        review {
                            totalCount
                            imageCount
                            avgRating
                            __typename
                        }
                        theme {
                            totalCount
                            __typename
                        }
                        isFollowing
                        followerCount
                        followRequested
                        __typename
                    }
                    body
                    thumbnail
                    media {
                        type
                        thumbnail
                        thumbnailRatio
                        class
                        videoId
                        videoUrl
                        trailerUrl
                        __typename
                    }
                    tags
                    status
                    visitCount
                    viewCount
                    visited
                    created
                    reply {
                        editUrl
                        body
                        editedBy
                        created
                        date
                        replyTitle
                        isReported
                        isSuspended
                        status
                        __typename
                    }
                    originType
                    item {
                        name
                        code
                        options
                        __typename
                    }
                    language
                    highlightOffsets
                    highlightRanges {
                        start
                        end
                        __typename
                    }
                    apolloCacheId
                    translatedText
                    businessName
                    showBookingItemName
                    bookingItemName
                    votedKeywords {
                        code
                        iconUrl
                        iconCode
                        displayName
                        name
                        __typename
                    }
                    userIdno
                    loginIdno
                    receiptInfoUrl
                    reactionStat {
                        id
                        typeCount {
                            name
                            count
                            __typename
                        }
                        totalCount
                        __typename
                    }
                    hasViewerReacted {
                        id
                        reacted
                        __typename
                    }
                    nickname
                    showPaymentInfo
                    visitKeywords {
                        code
                        category
                        keywords
                        __typename
                    }
                    visitCategories {
                        code
                        name
                        keywords {
                            code
                            name
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                starDistribution {
                    score
                    count
                    __typename
                }
                hideProductSelectBox
                total
                showRecommendationSort
                itemReviewStats {
                    score
                    count
                    itemId
                    starDistribution {
                        score
                        count
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
    """