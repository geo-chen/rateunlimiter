# rateunlimiter


## About

An open-source offensive tool to automatically get past the constraints of `Dynamic Rate-Limiters` to maximize the amount of unblocked hits delivered to the target endpoint(s).
Target audience: security researchers and red teamers.

## Problem

1. From an offensive standpoint, Rate-Limiters (RL) are getting more and more intelligent.
1. Rate thresholds, blocking method, threshold time bucket, and penalty period used to be static, i.e. for `>10hits/min on /login, block for 5min`
1. They have since evolved into what we call `Dynamic` Rate Limiters, where `dynamic` threshold values are used instead, i.e. `> z hits / y mins on endpoint x, block/challenge for p min`
1. Without being able to work out the rate thresholds, it’s difficult for offensive users to maximize their returns against rate-based limits, ie. bruteforcing
1. Current solutions only capable of (reverse) deriving threshold limits on `Static` Rate Limiters


## Visualize Dynamic RL
Here is an illustration of a use case of dynamic rate-limiter. For the given target endpoint of abc.com/login, there could be two overlapping threshold policies, policy 1 and policy 2. 
In the first iteration of policy 1, a rate threshold of 10hits/min could be presented with a blocking penalty of 3 mins and depending on the nature of traffic, it could pivot and dynamically change to 8 hits / 40secs, so on and so forth.

What this means is that if an attacker attempts to fly-below-the-radar and uses a constant rate of 9hits/min against this endpoint, he/she would not succeed against a dynamic ratelimiter after the first iteration.

Policy two might use a wider time bucket, and have the rate policies change dynamically as well. On top of that, if there should be any attempts against the endpoint while being blocked, the penalty period can be extended on a rolling basis. 
There are many more of such use cases, and they make reverse derivation of the rates extremely challenging.

![Dynamic RL](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss2.png?raw=true)


## Architecture Design
Here is a view on how the rateunlimiter can be placed. Whichever vehicle that carries the payload will pass the requests through the rateunlimiter, which will intelligently test and derive the highest and optimal rate of hit while keeping the friction level at the lowest. In the illustration below, usage of the rateunlimiter yields a lot more successful hits, for instance by maximizing the number of return code 200s as opposed to 429s. If it were vulnerability scanning, a lot more successful hits can be established for a given period of time based on the number of IPs available as a resource. 

![Design](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss3.png?raw=true)


## Eventual Architecture Design
This is the eventual design outside the timeframe of the HackSmith hackathon, wherein the rateunlimter would be the master node that continously derives the optimal thresholds and communicates that to the worker nodes to use against a given endpoint. The worker threads will obtain a new IP each time it's being blocked.

![Eventual](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss4.png?raw=true)

## Technical Layer
![Tech](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss5.png?raw=true)

## Burp Suite's IP Rotate with the rateunlimiter
The rateunlimiter script can easily be plugged into proxies for the rotation of IP addresses (multi-threaded on multiple IP addresses), such as [Burp Suite's IP Rotate extension](https://github.com/RhinoSecurityLabs/IPRotate_Burp_Extension). Just specify the `--proxy-host` and `--proxy-port` values!

![IP Rotate](https://github.com/spigeo/rateunlimiter/blob/main/Documentation/Images/ss1.png?raw=true)
