# rateunlimiter


## About

An open-source offensive tool to automatically get past the constraints of Dynamic RL to maximize the amount of unblocked hits delivered to the target endpoint(s).
Target audience: security researchers and red teamers.

## Problem

1. From an offensive standpoint, Rate-Limiters (RL) are getting more and more intelligent.
1. Rate thresholds, blocking method, threshold time bucket, and penalty period used to be static, i.e. for `>10hits/min on /login, block for 5min`
1. They have since evolved into what we call `Dynamic` Rate Limiters, where `dynamic` threshold values are used instead, i.e. `> z hits / y mins on endpoint x, block/challenge for p min`
1. Without being able to work out the rate thresholds, it’s difficult for offensive users to maximize their returns against rate-based limits, ie. bruteforcing
1. Current solutions only capable of (reverse) deriving threshold limits on `Static` Rate Limiters


![IP Rotate](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss1.png?raw=true)
