import duckdb
from ipykernel.kernelbase import Kernel

from decoy.cli_io import exception_list
from decoy.database import get_connection
from decoy.udf_scalar import clear_column_cache


class DecoyKernel(Kernel):
    implementation = "Decoy"
    implementation_version = "0.1"
    language = "SQL"
    language_version = "0.1"
    language_info = {
        "name": "SQL",
        "mimetype": "application/sql",
        "file_extension": ".sql",
    }
    banner = "Decoy - DuckDB with some useful synthetic data functions"

    def display_dataframe(self, df):
        stream_content = {
            "data": {
                "text/plain": df.to_string(),
                "text/html": df.to_html(),
            },
            "metadata": {},
            "transient": {},
        }
        self.send_response(self.iopub_socket, "display_data", content=stream_content)

    def get_display_error(self, ex):
        return {
            "ename": "Error",
            "evalue": str(ex),  # Exception value, as a string
            "traceback": [],  # traceback frames as strings
            "execution_count": self.execution_count,
        }

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        con = get_connection()
        clear_column_cache()
        try:
            con.execute(code)
        except exception_list as e:
            errdata = self.get_display_error(e)
            self.send_response(self.iopub_socket, "error", content=errdata)
            errdata["execution_count"] = self.execution_count
            errdata["status"] = "error"
            return errdata

        try:
            res = con.fetch_df()
        except duckdb.InvalidInputException as e:
            errdata = self.get_display_error(e)
            self.send_response(self.iopub_socket, "error", content=errdata)
            errdata["execution_count"] = self.execution_count
            errdata["status"] = "error"
            return errdata

        if not silent:
            self.display_dataframe(res)

        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=DecoyKernel)
