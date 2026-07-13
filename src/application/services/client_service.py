import json
from pathlib import Path
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup

from src.domain.models.client import Client
from src.domain.exceptions import DuplicateEntityException, EntityNotFoundException
from src.ports.inbound.client_service_port import ClientServicePort
from src.ports.outbound.client_repository_port import ClientRepositoryPort


class ClientService(ClientServicePort):
    """Implementation of ClientServicePort for client registration and import."""

    def __init__(self, client_repo: ClientRepositoryPort):
        self.client_repo = client_repo

    def register_client(self, nombre: str, cedula: str, proceso_desempeno: str, valor_a_descontar: float) -> Client:
        cedula_clean = str(cedula).strip()
        existing = self.client_repo.find_by_cedula(cedula_clean)
        if existing:
            raise DuplicateEntityException(f"Ya existe un cliente registrado con la cédula '{cedula_clean}'.")

        client = Client(
            nombre=nombre.strip(),
            cedula=cedula_clean,
            proceso_desempeno=proceso_desempeno.strip(),
            valor_a_descontar=float(valor_a_descontar)
        )
        return self.client_repo.save(client)

    def update_client(self, client_id: int, nombre: str, cedula: str, proceso_desempeno: str, valor_a_descontar: float) -> Client:
        client = self.client_repo.find_by_id(client_id)
        if not client:
            raise EntityNotFoundException(f"No se encontró el cliente con ID {client_id}.")

        cedula_clean = str(cedula).strip()
        if cedula_clean != client.cedula:
            existing = self.client_repo.find_by_cedula(cedula_clean)
            if existing and existing.id != client_id:
                raise DuplicateEntityException(f"La cédula '{cedula_clean}' ya está en uso por otro cliente.")

        client.nombre = nombre.strip()
        client.cedula = cedula_clean
        client.proceso_desempeno = proceso_desempeno.strip()
        client.valor_a_descontar = float(valor_a_descontar)
        return self.client_repo.save(client)

    def get_client(self, client_id: int) -> Optional[Client]:
        return self.client_repo.find_by_id(client_id)

    def get_client_by_cedula(self, cedula: str) -> Optional[Client]:
        return self.client_repo.find_by_cedula(str(cedula).strip())

    def list_clients(self, search_query: str = "") -> List[Client]:
        return self.client_repo.list_all(search_query=search_query)

    def delete_client(self, client_id: int) -> bool:
        client = self.client_repo.find_by_id(client_id)
        if not client:
            raise EntityNotFoundException(f"No se encontró el cliente con ID {client_id}.")
        return self.client_repo.delete(client_id)

    def import_from_html_file(self, file_path: str) -> Tuple[int, int]:
        """Parse Consulta.html file and import clients into the database.
        
        Returns:
            Tuple[int, int]: (imported_count, skipped_count)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"El archivo HTML '{file_path}' no fue encontrado.")

        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        table = soup.find("table")
        if not table:
            return (0, 0)

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")

        imported = 0
        skipped = 0

        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) < 5:
                continue

            # cells[0] is row # index
            nombre = cells[1].get_text(strip=True)
            cedula = cells[2].get_text(strip=True)
            proceso = cells[3].get_text(strip=True)
            valor_raw = cells[4].get_text(strip=True)

            if not cedula or not nombre:
                skipped += 1
                continue

            try:
                valor = float(valor_raw.replace("$", "").replace(",", "").strip() or 0.0)
            except ValueError:
                valor = 0.0

            existing = self.client_repo.find_by_cedula(cedula)
            if existing:
                # Update existing client data if needed
                existing.nombre = nombre
                existing.proceso_desempeno = proceso
                existing.valor_a_descontar = valor
                self.client_repo.save(existing)
                skipped += 1
            else:
                new_client = Client(
                    nombre=nombre,
                    cedula=cedula,
                    proceso_desempeno=proceso,
                    valor_a_descontar=valor
                )
                self.client_repo.save(new_client)
                imported += 1

        return (imported, skipped)

    def import_from_json_file(self, file_path: str) -> Tuple[int, int]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"El archivo JSON {file_path} no existe.")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("El formato del archivo JSON debe ser una lista de clientes.")

        imported = 0
        skipped = 0

        for item in data:
            if not isinstance(item, dict):
                continue
            nombre = str(item.get("nombre") or "").strip()
            cedula = str(item.get("cedula") or "").strip()
            proceso = str(
                item.get("proceso_desempeno")
                or item.get("Porceso de Desempeno")
                or "Pool de Ambulancia"
            ).strip()

            if not cedula or not nombre:
                skipped += 1
                continue

            existing = self.client_repo.find_by_cedula(cedula)
            if existing:
                existing.nombre = nombre
                existing.proceso_desempeno = proceso
                self.client_repo.save(existing)
                skipped += 1
            else:
                new_client = Client(
                    nombre=nombre,
                    cedula=cedula,
                    proceso_desempeno=proceso,
                    valor_a_descontar=0.0
                )
                self.client_repo.save(new_client)
                imported += 1

        return (imported, skipped)
