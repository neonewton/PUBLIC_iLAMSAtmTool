Knowledge Base: System Administration Fundamentals
1. What a System Administrator (SysAdmin) Does

A system administrator:

Maintains computer systems so they are available, secure, and reliable

Ensures systems work as expected for users

Responds to incidents and operational issues

Core responsibilities:

System setup

Monitoring

Maintenance

Troubleshooting

Access control

2. What Is a “System”

A system is a combination of:

Hardware

Software

Configuration

Users

Data

Examples:

A server running an application

A workstation used by staff

A network service providing authentication

3. Operating Systems (OS)

An operating system:

Controls hardware resources

Runs applications

Manages users and permissions

Common OS categories:

Desktop OS

Server OS

Key admin concepts:

Processes

Memory

Storage

Users

Permissions

4. Users and Access Control

Users:

Represent people or services using the system

Access control defines:

What a user can do

What resources they can access

Common principles:

Least privilege (only give required access)

Role separation

[ User ]
   |
   v
[ Permission Check ]
   |
   v
[ Resource Access ]

5. Files and Directories

Files store data

Directories organize files

Admin responsibilities:

Ensure correct ownership

Ensure correct permissions

Prevent unauthorized access

Risks of poor file management:

Data leaks

Accidental deletion

System instability

6. Services and Processes

A process:

A running instance of a program

A service:

A long-running process providing a function

Often starts automatically

Admin tasks:

Start services

Stop services

Check service status

7. System Startup and Shutdown

Startup:

OS loads

Services start in order

System becomes available

Shutdown:

Services stop

Data is written to disk

Hardware powers off safely

Improper shutdown risks:

Data corruption

Service failure on restart

8. Monitoring and Health Checks

Monitoring answers:

Is the system running?

Is it performing as expected?

Common indicators:

CPU usage

Memory usage

Disk usage

Service status

Good practice:

Detect issues before users report them

9. Logs and Troubleshooting

Logs:

Records of system and application events

Logs help answer:

What happened?

When did it happen?

Why did it happen?

Troubleshooting approach:

Observe symptoms

Check logs

Identify recent changes

Test one change at a time

10. Configuration Management

Configuration:

Settings that control system behavior

Examples:

Network settings

Service settings

Security rules

Best practices:

Document changes

Change one thing at a time

Be able to revert

11. Security Fundamentals

Security goals:

Confidentiality

Integrity

Availability

Admin responsibilities:

Patch systems

Control access

Monitor suspicious activity

Common mistakes:

Shared accounts

Unpatched systems

Excessive permissions

12. Backup and Recovery

Backup:

A copy of important data

Recovery:

Restoring data after failure

Key questions:

What data is critical?

How often is it backed up?

How fast must it be restored?

13. Incident Response (Basic)

An incident:

Anything that disrupts normal system operation

Basic response steps:

Identify the issue

Reduce impact

Restore service

Document what happened

14. Change Management (Beginner Level)

A change:

Any modification to a system

Good change practice:

Know what you are changing

Know why you are changing it

Know how to undo it

15. Documentation

Documentation:

Written knowledge about systems

Should include:

System purpose

Configuration details

Known issues

Recovery steps

Benefits:

Reduces dependency on individuals

Speeds up troubleshooting

Improves handover

16. What This Knowledge Base Does NOT Cover

Advanced networking design

Vendor-specific tools

Automation frameworks

Cloud architecture

Scripting languages

17. Learning Mindset for Junior SysAdmins

Focus on understanding cause and effect

Ask:

What is the system doing?

What should it be doing?

What changed?

Learn by:

Observing

Testing safely

Reading logs

Asking questions

18. When to Ask for Help

Ask when:

You do not understand the impact of a change

The issue persists after basic checks

The system affects many users

Asking early prevents larger outages