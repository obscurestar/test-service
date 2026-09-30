SELECT format(
    'CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD %L',
    :'replication_password'
)
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'replicator')
\gexec

ALTER ROLE replicator WITH REPLICATION LOGIN PASSWORD :'replication_password';

CREATE TABLE IF NOT EXISTS public.ddl_audit (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_name text NOT NULL,
    command_tag text NOT NULL,
    object_type text,
    schema_name text,
    object_identity text,
    user_name text NOT NULL,
    command_text text NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE OR REPLACE FUNCTION public.audit_ddl_command()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.ddl_audit (
        event_name,
        command_tag,
        object_type,
        schema_name,
        object_identity,
        user_name,
        command_text
    )
    SELECT
        TG_EVENT,
        TG_TAG,
        command.object_type,
        command.schema_name,
        command.object_identity,
        session_user,
        current_query()
    FROM pg_event_trigger_ddl_commands() AS command;
END;
$$;

CREATE OR REPLACE FUNCTION public.audit_sql_drop()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.ddl_audit (
        event_name,
        command_tag,
        object_type,
        schema_name,
        object_identity,
        user_name,
        command_text
    )
    SELECT
        TG_EVENT,
        TG_TAG,
        dropped.object_type,
        dropped.schema_name,
        dropped.object_identity,
        session_user,
        current_query()
    FROM pg_event_trigger_dropped_objects() AS dropped;
END;
$$;

DROP EVENT TRIGGER IF EXISTS audit_ddl_command_end;
CREATE EVENT TRIGGER audit_ddl_command_end
    ON ddl_command_end
    EXECUTE FUNCTION public.audit_ddl_command();

DROP EVENT TRIGGER IF EXISTS audit_sql_drop;
CREATE EVENT TRIGGER audit_sql_drop
    ON sql_drop
    EXECUTE FUNCTION public.audit_sql_drop();